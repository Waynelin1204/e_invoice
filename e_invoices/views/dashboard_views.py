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
from django.db.models.functions import TruncMonth
from django.db.models import Sum


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


def dashboard(request):
	return render(request,'dashboard.html')

def company_total_amount(request):
    # 查詢並按照公司和稅別分組，計算每組的總金額
    result = (
        TWB2BMainItem.objects.values('company_id', 'tax_type')  # 加入 tax_type 作為分組
        .annotate(total_amount=Sum('total_amount'))
        .order_by('company_id', 'tax_type')  # 可以按公司和稅別排序
    )
    
    data = list(result)
    return JsonResponse(data, safe=False)

def tax_type_summary_by_company(request):
    company_id = request.GET.get('company_id')
    if not company_id:
        return JsonResponse({'error': '缺少 company_id'}, status=400)

    result = (
        TWB2BMainItem.objects
        .filter(company_id=company_id)
        .values('tax_type')
        .annotate(total_amount=Sum('total_amount'))
        .order_by('-total_amount')
    )
    return JsonResponse(list(result), safe=False)


def invoice_status(request):
    # 查詢所有發票並按公司與發票狀態進行分組
    invoices = TWB2BMainItem.objects.all()
    
    # 使用 annotate 來進行統計，並按公司和發票狀態分組
    company_status = []
    
    # 首先將所有發票依公司與狀態進行分組，並計算每個狀態下的發票數量
    for company in invoices.values('company_id').distinct():
        company_id = company['company_id']
        
        # 統計每個公司每個狀態的發票數量
        status_counts = (
            company_invoices := invoices.filter(company_id=company_id)
            .values('invoice_status')
            .annotate(invoice_count=Count('id'))
        )
        
        # 構建返回結果
        for status_count in status_counts:
            company_status.append({
                'company_id': company_id,
                'invoice_status': status_count['invoice_status'],
                'invoice_count': status_count['invoice_count'] or 0
            })
    
    return JsonResponse(company_status, safe=False)
