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
from e_invoices.models.uploadlog_models import UploadLog

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