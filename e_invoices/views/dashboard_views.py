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
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.utils.timezone import now
from datetime import timedelta, date

# ====== Django DB 操作 ======
from django.db import connection
from django.db import transaction
from django.db.models import Q, Count, F
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
    NumberDistribution, TWB2BMainItem, TWB2BLineItem, TWAllowance , TWAllowanceLineItem
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


# def invoice_status(request):
#     # 查詢所有發票並按公司與發票狀態進行分組
#     invoices = TWB2BMainItem.objects.all()
    
#     # 使用 annotate 來進行統計，並按公司和發票狀態分組
#     company_status = []
    
#     # 首先將所有發票依公司與狀態進行分組，並計算每個狀態下的發票數量
#     for company in invoices.values('company_id').distinct():
#         company_id = company['company_id']
        
#         # 統計每個公司每個狀態的發票數量
#         status_counts = (
#             company_invoices := invoices.filter(company_id=company_id)
#             .values('invoice_status')
#             .annotate(invoice_count=Count('id'))
#         )
        
#         # 構建返回結果
#         for status_count in status_counts:
#             company_status.append({
#                 'company_id': company_id,
#                 'invoice_status': status_count['invoice_status'],
#                 'invoice_count': status_count['invoice_count'] or 0
#             })
    
#     return JsonResponse(company_status, safe=False)


# def invoice_status(request):
#     today = now().date()

#     # 計算目前雙月期別（本期）與上一期（前期）
#     if today.month % 2 == 0:
#         current_start = date(today.year, today.month - 1, 1)
#         current_end = date(today.year, today.month, 1) + timedelta(days=31)
#         current_end = current_end.replace(day=1) - timedelta(days=1)
#     else:
#         current_start = date(today.year, today.month, 1)
#         current_end = current_start + timedelta(days=62)
#         current_end = current_end.replace(day=1) - timedelta(days=1)

#     previous_end = current_start - timedelta(days=1)
#     previous_start = (previous_end.replace(day=1) - timedelta(days=1)).replace(day=1)

#     # 僅取得有權限的公司資料
#     user_profile = request.user.profile
#     viewable_companies = user_profile.viewable_companies.all()
#     viewable_company_ids = viewable_companies.values_list('company_id', flat=True)
#     company_name_map = {c.company_id: c.company_name for c in viewable_companies}

#     invoices = TWB2BMainItem.objects.filter(company_id__in=viewable_company_ids)
#     allowances = TWAllowance.objects.filter(company_id__in=viewable_company_ids)

#     def get_stats(start_date, end_date):
#         invoice_stats = (
#             invoices.filter(erp_date__range=[start_date, end_date])
#             .values('company_id', 'invoice_status')
#             .annotate(
#                 invoice_count=Count('id'),
#                 total_amount=Sum('sales_amount')
#             )
#         )

#         # 折讓資料統計
#         allowance_stats_map = {}
#         allowance_stats = (
#             allowances.filter(allowance_date__range=[start_date, end_date])
#             .values('company_id', 'source_invoice_status')
#             .annotate(
#                 allowance_count=Count('id'),
#                 allowance_amount=Sum('allowance_amount')
#             )
#         )
#         for a in allowance_stats:
#             key = (a['company_id'], a['source_invoice_status'])
#             allowance_stats_map[key] = {
#                 'count': a['allowance_count'],
#                 'amount': a['allowance_amount']
#             }

#         # 整合資料
#         result = []
#         for item in invoice_stats:
#             company_id = item['company_id']
#             status = item['invoice_status']
#             key = (company_id, status)
#             item['company_name'] = company_name_map.get(company_id, '')
#             item['allowance_count'] = allowance_stats_map.get(key, {}).get('count', 0)
#             item['allowance_amount'] = allowance_stats_map.get(key, {}).get('amount', 0)
#             result.append(item)
#         return result

#     result = {
#         "current": get_stats(current_start, current_end),
#         "previous": get_stats(previous_start, previous_end)
#     }

#     return JsonResponse(result, safe=False)


def invoice_status(request):
    today = now().date()

    # 計算目前雙月期別（本期）與上一期（前期）
    if today.month % 2 == 0:
        current_start = date(today.year, today.month - 1, 1)
        current_end = date(today.year, today.month, 1) + timedelta(days=31)
        current_end = current_end.replace(day=1) - timedelta(days=1)
    else:
        current_start = date(today.year, today.month, 1)
        current_end = current_start + timedelta(days=62)
        current_end = current_end.replace(day=1) - timedelta(days=1)

    previous_end = current_start - timedelta(days=1)
    previous_start = (previous_end.replace(day=1) - timedelta(days=1)).replace(day=1)

    # 僅取得有權限的公司資料
    user_profile = request.user.profile
    viewable_companies = user_profile.viewable_companies.all()
    viewable_company_ids = viewable_companies.values_list('company_id', flat=True)
    company_name_map = {c.company_id: c.company_name for c in viewable_companies}

    invoices = TWB2BMainItem.objects.filter(company_id__in=viewable_company_ids)
    allowances = TWAllowance.objects.filter(company_id__in=viewable_company_ids)

    def get_stats(start_date, end_date):
        invoice_stats = (
            invoices.filter(erp_date__range=[start_date, end_date])
            .values('company_id', 'invoice_status')
            .annotate(
                invoice_count=Count('id'),
                total_amount=Sum('total_amount'),
                total_tax_amount=Sum('total_tax_amount')
            )
        )

        allowance_stats = (
            allowances.filter(erp_date__range=[start_date, end_date])
            .values('company_id', 'allowance_status')
            .annotate(
                invoice_status=F('allowance_status'),
                allowance_count=Count('id'),
                allowance_amount=Sum('allowance_amount'),
                allowance_tax=Sum('allowance_tax')
            )
        )

        combined_stats = {}

        for inv in invoice_stats:
            key = (inv['company_id'], inv['invoice_status'])
            combined_stats[key] = {
                'company_id': inv['company_id'],
                'invoice_status': inv['invoice_status'],
                'invoice_count': inv['invoice_count'],
                'total_amount': inv['total_amount'],
                'total_tax_amount': inv['total_tax_amount'],
                'allowance_count': 0,
                'allowance_amount': 0,
                'allowance_tax': 0,
                'company_name': company_name_map.get(inv['company_id'], '')
            }

        for allow in allowance_stats:
            key = (allow['company_id'], allow['invoice_status'])
            if key not in combined_stats:
                combined_stats[key] = {
                    'company_id': allow['company_id'],
                    'invoice_status': allow['invoice_status'],
                    'invoice_count': 0,
                    'total_amount': 0,
                    'allowance_count': allow['allowance_count'],
                    'allowance_amount': allow['allowance_amount'],
                    'allowance_tax': allow['allowance_tax'],
                    'company_name': company_name_map.get(allow['company_id'], '')
                }
            else:
                combined_stats[key]['allowance_count'] = allow['allowance_count']
                combined_stats[key]['allowance_amount'] = allow['allowance_amount']
                combined_stats[key]['allowance_tax'] = allow['allowance_tax'] 

        return list(combined_stats.values())

    result = {
        "current": get_stats(current_start, current_end),
        "previous": get_stats(previous_start, previous_end),
        "period_range": {
            "current": f"{current_start.month:02d}-{current_end.month:02d}",
            "previous": f"{previous_start.month:02d}-{previous_end.month:02d}"
            }
    }

    return JsonResponse(result, safe=False)
