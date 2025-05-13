# ====== Python 標準函式庫 ======
import os
import re
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


# 營業人管理
def company_detail(request):
    companies = Company.objects.all()
    return render(request, 'company_detail.html', {'companies': companies})    

# 營業人管理-檢視+修改
def company_detail_sub(request, company_id):
    print("Received company_id:", company_id)
    company = get_object_or_404(Company, company_id=company_id)
    head_offices = Company.objects.filter(company_type=0).exclude(company_id=company.company_id)

    if request.method == 'POST':
        # 抓取表單值
        company_register_name = request.POST.get('company_register_name', '').strip()
        company_identifier = request.POST.get('company_identifier', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        company_address = request.POST.get('company_address', '').strip()
        company_type = request.POST.get('company_type')
        is_foreign_ecomm = request.POST.get('is_foreign_ecomm')
        tax_identifer = request.POST.get('tax_identifer', '').strip()
        email = request.POST.get('email', '').strip()
        reporting_period = request.POST.get('reporting_period')
        head_id = request.POST.get('head_company_identifer')

        errors = {}
        # 後端驗證
        if not re.fullmatch(r'^\d{8}$', company_identifier):
            errors['company_identifier'] = '請輸入8碼數字'
        
        if len(company_register_name) > 100:
            errors['company_register_name'] = '請輸入100碼以內字元'

        if len(company_name) > 100:
            errors['company_name'] = '請輸入100碼以內字元'

        if len(company_address) > 255:
            errors['company_address'] = '請輸入255碼以內字元'

        if not re.fullmatch(r'^\d{9}$', tax_identifer):
            errors['tax_identifer'] = '請輸入9碼數字'

        if email and not re.fullmatch(r'^.+@.+$', email):
            errors['email'] = '請輸入100碼以內含有「@」符號的電子郵件地址'

        if errors:
            head_offices = Company.objects.filter(company_type=0)
            form_data = request.POST.dict()
            return render(request, 'company_detail_sub.html', {
                'head_offices': head_offices,
                'errors': errors,
                'form_data': form_data
            })
        
        # 通過驗證才儲存
        company.company_register_name = company_register_name
        company.company_identifier = company_identifier
        company.company_name = company_name
        company.company_address = company_address
        company.company_type = int(company_type)
        company.is_foreign_ecomm = int(is_foreign_ecomm)
        company.tax_identifer = tax_identifer
        company.email = email
        company.reporting_period = reporting_period

        if head_id:
            company.head_company_identifer = Company.objects.get(id=head_id)
        else:
            company.head_company_identifer = None

        company.save()

        messages.success(request, '營業人資料儲存成功！')
        return redirect('company_detail_sub', company_id=company_id)

    return render(request, 'company_detail_sub.html', {
        'company': company,
        'head_offices': head_offices,
    })

# 營業人管理 - 新增
def company_add(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id', '').strip()
        company_identifier = request.POST.get('company_identifier', '').strip()
        company_register_name = request.POST.get('company_register_name', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        company_address = request.POST.get('company_address', '').strip()
        head_company_identifer_id = request.POST.get('head_company_identifer') or None
        company_type = request.POST.get('company_type')
        is_foreign_ecomm = request.POST.get('is_foreign_ecomm')
        tax_identifer = request.POST.get('tax_identifer', '').strip()
        email = request.POST.get('email', '').strip()
        reporting_period = request.POST.get('reporting_period')

        errors = {}
        # 後端驗證
        if not re.fullmatch(r'^[a-zA-Z0-9]{1,10}$', company_id):
            errors['company_id'] = '請輸入10碼以內字元，僅限英文大小寫或數字'
        elif Company.objects.filter(company_id=company_id).exists():
            errors['company_id'] = '營業人代碼已存在，請重新輸入'

        if not re.fullmatch(r'^\d{8}$', company_identifier):
            errors['company_identifier'] = '請輸入8碼數字'
        
        if len(company_register_name) > 100:
            errors['company_register_name'] = '請輸入100碼以內字元'

        if len(company_name) > 100:
            errors['company_name'] = '請輸入100碼以內字元'

        if len(company_address) > 255:
            errors['company_address'] = '請輸入255碼以內字元'

        if not re.fullmatch(r'^\d{9}$', tax_identifer):
            errors['tax_identifer'] = '請輸入9碼數字'

        if email and not re.fullmatch(r'^.+@.+$', email):
            errors['email'] = '請輸入100碼以內含有「@」符號的電子郵件地址'

        if errors:
            head_offices = Company.objects.filter(company_type=0)
            form_data = request.POST.dict()
            return render(request, 'company_add.html', {
                'head_offices': head_offices,
                'errors': errors,
                'form_data': form_data
            })

        # 若驗證通過，建立資料
        Company.objects.create(
            company_id=company_id,
            company_identifier=company_identifier,
            company_register_name=company_register_name,
            company_name=company_name,
            company_address=company_address,
            head_company_identifer_id=head_company_identifer_id,
            company_type=company_type,
            is_foreign_ecomm=is_foreign_ecomm,
            tax_identifer=tax_identifer,
            email=email,
            reporting_period=reporting_period,
        )
        messages.success(request, '營業人資料儲存成功！')
        return redirect('company_detail')

    head_offices = Company.objects.filter(company_type=0)
    return render(request, 'company_add.html', {
        'head_offices': head_offices,
        'form_data': {},
        'errors': {}
    })
    
# 統一編號檢查碼邏輯
def validateUniformNumberTW(value: str) -> bool:
    if not re.fullmatch(r'^\d{8}$', value):
        return False

    multipliers = [1, 2, 1, 2, 1, 2, 4, 1]
    total = 0

    for i in range(8):
        product = int(value[i]) * multipliers[i]
        total += product // 10 + product % 10

    # 特例：第7碼是7且 total+1 可被5整除
    if value[6] == '7' and (total + 1) % 5 == 0:
        return True

    return total % 5 == 0