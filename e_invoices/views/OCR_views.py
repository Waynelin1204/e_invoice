# ====== Python 標準函式庫 ======
import os
import json
import logging
import subprocess
from io import BytesIO
from datetime import datetime, timedelta
from collections import defaultdict
import xml.etree.ElementTree as ET

# ====== 第三方套件 ======
import pandas as pd
from openpyxl import load_workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ====== Django 基礎功能 ======
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils import timezone

# ====== Django DB 操作 ======
from django.db import connection
from django.db import transaction
from django.db.models import Q, Count

# ====== Django 使用者與驗證 ======
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test

# ====== 專案內部（Model 與 Form） ======
from e_invoices.models import (
    RegisterForm, LoginForm,
    Twa0101, Twa0101Item, Ocr, Ocritem, Company, UserProfile,
    NumberDistribution, TWB2BMainItem, TWB2BLineItem
)
from e_invoices.forms import NumberDistributionForm




UPLOAD_DIR = "/home/pi/OCR/Samples"
@csrf_exempt
def upload_file(request):
    
    if request.method == "POST":
        if "file" not in request.FILES:
            return JsonResponse({"success":False, "error": "Didn't Receive"}, status=400)

        file = request.FIELS["file"]
        file_path = os.path.join(UPLOAD_DIR, file.name)

        try:
            with open(file_path, "wb") as f:
                 for chunk in file.chunks():
                     f.write(chunk)
		
            return JsonResponse({"success":True, "file_path": file_path})
        except Exception as e:
            return JsonResponse({"success":False, "error": str(e)}, status=500)
    return JsonResponse({"success":False, "error": "Invalid"}, status=400)

@csrf_exempt    
def run_script(request):
    """Execute the OCR script and return output as JSON."""
    if request.method == "POST":
        try:
            script_output = subprocess.check_output(["python3", "/home/pi/OCR/AWS_PARSE_multi.py"], text=True)
            return JsonResponse({"success": True, "output": script_output})
        except subprocess.CalledProcessError as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


def invoice_list(request):
    invoices = Ocr.objects.all()  # Fetch all invoices
    
    search_query = request.GET.get('search', '')
    if search_query:
        invoices = invoices.filter(invoice_number__icontains=search_query)
    return render(request, 'invoices/invoice_list.html', {'invoices': invoices})



def invoice_detail(request, invoice_id):
    invoice = Ocr.objects.get(id=invoice_id)  # Fetch a specific invoice
    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})

def update_invoice_status(request):
    if request.method == 'POST':
        selected_id = request.POST.get("selected_documents", "").split(",")

        # 確保發票號碼有效
        selected_id = [num.strip() for num in selected_id if num.strip()]
        
        if selected_id:
            updated_count = Twa0101.objects.filter(id__in=selected_id).update(invoice_status='已開立')
            print(f"更新了 {updated_count} 筆發票")
        else:
            print("沒有選中的發票")

    return redirect('test')  # 替換為您的發票列表頁面名稱

def invoice_filter(request):
    # 預設顯示筆數
    display_limit = int(request.GET.get("display_limit", 20))  # 默認為20筆資料

    # 其他篩選條件
    invoice_status_filter = request.GET.get("invoice_status")
    void_status_filter = request.GET.get("void_status")
    tax_type_filter = request.GET.get("tax_type")

    # 計算兩個月前的日期
    two_months_ago = datetime.today() - timedelta(days=60)

    # 取得時間範圍的過濾條件（默認從兩個月前開始）
    start_date = request.GET.get("start_date", two_months_ago.strftime('%Y-%m-%d'))
    end_date = request.GET.get("end_date", datetime.today().strftime('%Y-%m-%d'))

    # 轉換成 datetime 格式
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    except ValueError:
        start_date = two_months_ago  # 如果格式錯誤，使用預設的兩個月前日期

    try:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        end_date = datetime.today()  # 如果格式錯誤，使用今天的日期

    if (end_date - start_date).days > 60:
        messages.error(request, "查詢區間不得超過 60 天")
        return redirect('test')
    if start_date > end_date:
        messages.error(request, "開始日期不能大於結束日期")
        return redirect('test')
    
    # 查詢條件構建
    filters = Q()
    if invoice_status_filter:
        filters &= Q(invoice_status=invoice_status_filter)
    if void_status_filter:
        filters &= Q(void_status=void_status_filter)
    if tax_type_filter:
        filters &= Q(tax_type=tax_type_filter)

    # 限制在兩個月前到今天的時間範圍內
    filters &= Q(invoice_date__range=[start_date, end_date])

    # 查詢所有符合條件的發票資料
    invoices_list = Twa0101.objects.filter(filters).order_by('-invoice_date')

    # 分頁
    paginator = Paginator(invoices_list, display_limit)  # 每頁顯示的資料筆數
    page_number = request.GET.get('page')  # 獲取當前頁碼
    page_obj = paginator.get_page(page_number)  # 根據頁碼獲取相應的頁面資料

    # 獲取篩選條件的選項
    invoice_status = Twa0101.objects.values_list('invoice_status', flat=True).distinct()
    void_status = Twa0101.objects.values_list('void_status', flat=True).distinct()
    tax_type = Twa0101.objects.values_list('tax_type', flat=True).distinct()

    return render(request, "test.html", {
        "invoice_status": invoice_status,
        "void_status": void_status,
        "tax_type": tax_type,
        "display_limit": display_limit,  # 傳遞選擇的筆數
        "documents": page_obj,  # 傳遞分頁結果
        "start_date": start_date.strftime('%Y-%m-%d'),  # 顯示篩選的開始日期
        "end_date": end_date.strftime('%Y-%m-%d'),  # 顯示篩選的結束日期
    })