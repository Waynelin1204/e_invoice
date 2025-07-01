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
from django.views.decorators.csrf import csrf_exempt

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

# ====== 專案內部 ======
from e_invoices.services.parse_services import process_data
from e_invoices.services.parse_response_service import process_all_processresult_xml
from e_invoices.models.uploadlog_models import UploadLog

from datetime import datetime, timedelta
from e_invoices.models import TWB2BMainItem
from e_invoices.services import send_invoice_summary_to_customer_email

def import_log(request):
    # 從資料庫中查詢匯入記錄
    logs = UploadLog.objects.all().order_by('-upload_time')  # 根據上傳時間排序
    return render(request, 'import_log.html', {'logs': logs})

UPLOAD_DIR_TW = os.path.join(settings.BASE_DIR, "upload") 

def upload(request):
    # 取得該使用者可查看的公司名稱列表
    user_profile = request.user.profile
    
    # 查詢符合條件的資料，並使用 prefetch_related 來查詢發票明細
    company_options = user_profile.viewable_companies.all()
    form_data = {}

    if request.method == 'POST':
        form_data = {
            'company_id': request.POST.get('company_id', '').strip(),
            'b2b_b2c': request.POST.get('b2b_b2c', '').strip(),
            'import_type': request.POST.get('import_type', '').strip(),
        }

    context = {
        'company_options': company_options,
        'form_data': form_data,
    }
    return render(request, 'upload_invoice.html', context)


@csrf_exempt
def upload_file_tw(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "無效的請求方式，請使用 POST"}, status=405)

    uploaded_file = request.FILES.get("upload_file")
    if not uploaded_file:
        return JsonResponse({"success": False, "error": "沒有收到檔案"}, status=400)

    # 檢查副檔名
    allowed_extensions = ['.xlsx', '.xls', '.csv']
    _, ext = os.path.splitext(uploaded_file.name.lower())
    if ext not in allowed_extensions:
        return JsonResponse({
            "success": False,
            "error": "請上傳副檔名為 .xlsx、.xls 或 .csv 的檔案"
        }, status=400)

    # 儲存檔案
    os.makedirs(UPLOAD_DIR_TW, exist_ok=True)
    save_path = os.path.join(UPLOAD_DIR_TW, uploaded_file.name)

    try:
        with open(save_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        return JsonResponse({
            "success": True,
            "file_path": save_path,
            "file_name": uploaded_file.name
        })

    except Exception as e:
        return JsonResponse({"success": False, "error": f"儲存檔案失敗：{str(e)}"}, status=500)


@csrf_exempt
def run_script_tw(request):
    """執行資料解析"""
    if request.method == "POST":
        try:
            # 解析 JSON 資料
            data = json.loads(request.body.decode("utf-8"))
            company_id = data.get("company_id")
            b2b_b2c = data.get("b2b_b2c")
            import_type = data.get("import_type")
            file_name = data.get("file_name")
            if not file_name: # 用file_name組出完整檔案路徑
                return JsonResponse({"success": False, "error": "缺少檔案名稱"}, status=400)

            file_path = os.path.join(UPLOAD_DIR_TW, file_name)

            result = process_data(file_path, company_id, b2b_b2c, import_type, request.user.username)
            # return JsonResponse({"success": True, **result})
            return JsonResponse({
                "success": True,
                "file_path": file_path,
                "file_name": file_name  # 加這行
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@csrf_exempt
def run_script_response(request):
    process_all_processresult_xml()
    return HttpResponse("已處理完畢")
@csrf_exempt
def auto_send_invoice_summary_email(request):
    """
    搜尋 TWB2BMainItem 符合條件的資料並自動寄信
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2)

    # 查詢兩天內 mof_reason = 'S0001' 的主表資料
    queryset = TWB2BMainItem.objects.filter(
        mof_response="S0001",
        invoice_date__range=(start_date, end_date)
    )
    print(queryset)

    for invoice in queryset:
        items = invoice.items.all()
        if not items.exists():
            print(f"ID {invoice.id} 無明細資料，已跳過")
            continue

        item = items.first()

        # 呼叫寄信函式
        send_invoice_summary_to_customer_email(
            to_email=invoice.buyer_email,
            invoice = invoice,
            company_name = invoice.company.company_name,
            company_identifier = invoice.company.company_identifier,
            company_address = invoice.company.company_address,
            buyer_name=invoice.buyer_name,
            invoice_number = invoice.invoice_number,
            invoice_date=invoice.invoice_date,
            invoice_time=invoice.invoice_time if invoice.invoice_time else '',
            random_code=invoice.random_code,
            total_amount=invoice.total_amount,
            buyer_identifier=invoice.buyer_identifier,
            line_description=item.line_description,
            line_quantity=item.line_quantity,
            unit_price=item.line_unit_price
        )

        print(f"已寄出發票通知給 {invoice.buyer_email}")
    return HttpResponse("已處理完畢")