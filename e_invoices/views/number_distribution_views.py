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

def number_distribution(request):
    # 取得所有發票號碼的狀態
    numbers = NumberDistribution.objects.all()
    return render(request, 'number_distribution.html', {'numbers':numbers})

def create_number_distribution(request):
    if request.method == 'POST':
        form = NumberDistributionForm(request.POST)
        form.fields['company'].queryset = Company.objects.all()  # <-- 必加在 POST 裡也加
        if form.is_valid():
            form.save()
            return redirect('create_number_distribution')  # 或導向你要的成功頁面
        else:
            print(form.errors)
    else:

        form = NumberDistributionForm()
    form.fields['company'].queryset = Company.objects.all()  # <--- 必加

    return render(request, 'create_number_distribution.html', {'form': form})


@csrf_exempt
def get_next_invoice_number(distribution):
    try:
        if distribution.current_number:
            next_number = int(distribution.current_number) + 1
        else:
            next_number = int(distribution.start_number)

        if next_number > int(distribution.end_number):
            raise ValueError(f"號碼區間已用完：{distribution.initial_char}{distribution.end_number}")

        return str(next_number).zfill(len(distribution.start_number))

    except ValueError as e:
        raise e
    except Exception:
        raise ValueError("發號時發生非預期錯誤")
