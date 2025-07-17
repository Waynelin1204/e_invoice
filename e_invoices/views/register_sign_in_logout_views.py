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
from e_invoices.forms import LoginForm
from e_invoices.models import (
    RegisterForm, LoginForm,
    Twa0101, Twa0101Item, Ocr, Ocritem, Company, UserProfile,
    NumberDistribution, TWB2BMainItem, TWB2BLineItem
)
from e_invoices.forms import NumberDistributionForm
@csrf_exempt
def register(request):

    form = RegisterForm()

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    context = {
        'form':form
    }
    return render(request, 'accounts/register.html', context)
@csrf_exempt
def sign_in(request):

    #form=LoginForm()
    error_message = None  # ✅ 初始化
    #form = AuthenticationForm()

    # if request.method == "POST":
    #     username = request.POST.get("username")
    #     password = request.POST.get("password")
    #     user = authenticate(request, username=username, password=password)
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('main')
            else:
                error_message = "帳號或密碼錯誤，請重新輸入"
    else:
        form = LoginForm()

    return render(request, 'login.html', {
        'form': form,
        'error_message': error_message
    })
    #     if user is not None:
    #         login(request, user)
    #         return redirect('main') # ✅ Corrected
    #     else:
    #         error_message = "帳號或密碼錯誤，請重新輸入"


    # context = {
    #     'form': form,
    #     'error_message': error_message
    # }
    # return render(request, 'login.html', context)


@csrf_exempt
def logout(request):
	logout(request)
	return redirect('/login.html')