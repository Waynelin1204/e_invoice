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

UPLOAD_DIR_TW = os.path.join(settings.BASE_DIR, "upload") 

def upload_test(request):
    user_profile = request.user.profile
    
    # 取得該使用者可查看的公司名稱列表
    
    # 查詢符合條件的資料，並使用 prefetch_related 來查詢發票明細
    company_options = user_profile.viewable_companies.all()
    context = {
        "company_options": company_options,
    }

    return render(request, 'upload_test.html',context)


@csrf_exempt
def upload_file_tw(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("invoice_file")

        if not uploaded_file:
            return JsonResponse({"success": False, "error": "沒有收到檔案"}, status=400)

        os.makedirs(UPLOAD_DIR_TW, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR_TW, uploaded_file.name)

        try:
            with open(file_path, "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            return JsonResponse({"success": True, "file_path": file_path})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "無效的請求"}, status=400)

@csrf_exempt
def run_script_tw(request):
    """Execute the parse.py script which handles Excel to DB import."""
    parse_script_path = os.path.join(UPLOAD_DIR_TW, "import2sqlite.py")
    
    if request.method == "POST":
        try:
            # 執行 parse.py 腳本（Python 版本依實際情況調整：python 或 python3）
            script_output = subprocess.check_output(["python", parse_script_path], text=True)

            return JsonResponse({"success": True, "output": script_output})

        except subprocess.CalledProcessError as e:
            return JsonResponse({"success": False, "error": str(e.output)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)