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

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def manage_user_permissions(request):
    all_users = User.objects.all()
    # companies = {company.id: f"{company.company_id} - {company.company_name}" for company in Company.objects.all()}  
    companies = {company.company_id: f"{company.company_id} - {company.company_name}" for company in Company.objects.all()} 
    return render(request, "permissions.html", {"all_users": all_users, "companies": json.dumps(companies)})

@login_required
@user_passes_test(is_admin)
def get_user_permissions(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)

        # 確保 UserProfile 存在
        user_profile, _ = UserProfile.objects.get_or_create(user=user)

        # 取得該使用者已選取的公司
        # viewable_companies = list(user_profile.viewable_companies.values_list("id", flat=True))
        viewable_companies = list(user_profile.viewable_companies.values_list("company_id", flat=True))


        return JsonResponse({"status": "exists", "viewable_companies": viewable_companies})

    except Exception as e:
        return JsonResponse({"status": "error", "message": f"發生錯誤: {str(e)}"})
    

# **更新使用者的可查看公司權限**
@csrf_exempt  # 這裡使用 @csrf_exempt 來免除 CSRF 檢查，視情況而定可選擇開啟 CSRF 檢查
@login_required
@user_passes_test(is_admin)
def update_permissions(request, user_id):
    if request.method == "POST":
        try:
            user = get_object_or_404(User, id=user_id)
            user_profile, _ = UserProfile.objects.get_or_create(user=user)

            # 解析前端傳過來的 JSON 資料
            data = json.loads(request.body)
            selected_companies = data.get("viewable_companies", [])

            # 確保傳入的 ID 是有效的
            # valid_companies = Company.objects.filter(id__in=selected_companies)
            valid_companies = Company.objects.filter(company_id__in=selected_companies)
            
            # 更新使用者的 viewable_companies 權限
            user_profile.viewable_companies.set(valid_companies)

            return JsonResponse({"status": "success", "message": "權限更新成功！"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": f"發生錯誤: {str(e)}"})

    return JsonResponse({"status": "error", "message": "無效的請求"}, status=400)