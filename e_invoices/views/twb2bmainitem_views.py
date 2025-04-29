# ====== Python 標準函式庫 ======
import os
import json
import logging
import subprocess
from io import BytesIO
from datetime import datetime, timedelta
from collections import defaultdict
import xml.etree.ElementTree as ET
from django.utils.timezone import localtime
from decimal import Decimal, InvalidOperation

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

@login_required
def twb2bmainitem(request):
    # 取得登入使用者的 UserProfile
    user_profile = request.user.profile
    
    # 取得該使用者可查看的公司名稱列表
    #viewable_company_codes = user_profile.viewable_companies.values_list('id', flat=True)
    viewable_company_codes = user_profile.viewable_companies.values_list('company_id', flat=True)

    
    # 計算從今天開始往前推的60天的日期
    sixty_days_ago = datetime.today() - timedelta(days=60)
    
    # 篩選條件：只顯示最近60天的發票
    filter_conditions = Q(company__in=viewable_company_codes) & Q(erp_date__gte=sixty_days_ago)

    # 查詢符合條件的資料，並使用 prefetch_related 來查詢發票明細
    documents = TWB2BMainItem.objects.filter(filter_conditions).prefetch_related('items').order_by('-erp_date')
    company_options = user_profile.viewable_companies.all()



    for document in documents:
        document.is_disabled = (
            document.invoice_status == '已作廢' or
            (
                document.tax_type == '2' and (
                    (document.zerotax_sales_amount or 0) <= 0 or
                    not document.customs_clearance_mark or
                    not document.bonded_area_confirm or
                    not document.zero_tax_rate_reason
                )
            )
        )

    # 分頁：每頁顯示25筆資料
    paginator = Paginator(documents, 25)  # 每頁顯示25筆資料
    page_number = request.GET.get('page')  # 取得當前頁數
    page_obj = paginator.get_page(page_number)  # 根據頁數取得對應的資料

    # 傳遞資料給模板
    context = {
        'documents': page_obj,  # 傳遞分頁後的資料
        "company_options": company_options,
    }
    print("🔍 可查看的公司 company_id：", list(viewable_company_codes))
    print("✅ 撈到的發票數：", TWB2BMainItem.objects.filter(filter_conditions).count())
    print("🟡 viewable_company_ids:", list(viewable_company_codes))
    print("🟡 篩選時間從:", sixty_days_ago)
    #print("🟡 所有發票的公司代碼：", TWB2BMainItem.objects.values_list("company_code", flat=True).distinct())
    print("🟡 所有發票的公司代碼：", TWB2BMainItem.objects.values_list("company_id", flat=True).distinct())    
    print("🟡 最近60天的發票：", TWB2BMainItem.objects.filter(erp_date__gte=sixty_days_ago).values_list("company_id", flat=True))
    print("🟡 完整符合條件的發票數：", TWB2BMainItem.objects.filter(filter_conditions).count())

    return render(request, 'twb2bmainitem.html', context)

#======================================================B2B發票明細=======================================================
    
def twb2blineitem(request, id):
    document = get_object_or_404(TWB2BMainItem, id=id)
    items = document.items.all()  # 確保有正確查詢
    return render(request, 'document/twb2blineitem.html', {'document': document, 'items': items})

def twb2blineitem_update(request, id):
    document = get_object_or_404(TWB2BMainItem, id=id)
    if request.method == 'POST':
        # 處理主項目資料
        invoice_period = request.POST.get('invoice_period', '').strip()
        erp_reference = request.POST.get('erp_reference', '').strip()
        seller_bp_id = request.POST.get('seller_bp_id', '').strip()
        buyer_bp_id = request.POST.get('buyer_bp_id', '').strip()
        buyer_remark = request.POST.get('buyer_remark', '').strip()
        main_remark = request.POST.get('main_remark', '').strip()
        customs_clearance_mark = request.POST.get('customs_clearance_mark', '').strip()
        category = request.POST.get('category', '').strip()
        relate_number = request.POST.get('relate_number', '').strip()
        bonded_area_confirm = request.POST.get('bonded_area_confirm', '').strip()
        zero_tax_rate_reason = request.POST.get('zero_tax_rate_reason', '').strip()
        reserved1 = request.POST.get('reserved1', '').strip()
        reserved2 = request.POST.get('reserved2', '').strip()
        try:
            original_currency_amount = Decimal(request.POST.get('original_currency_amount', '').strip()) if request.POST.get('original_currency_amount', '').strip() else None
        except InvalidOperation:
            original_currency_amount = None
        try:
            exchange_rate = Decimal(request.POST.get('exchange_rate', '').strip()) if request.POST.get('exchange_rate', '').strip() else None
        except InvalidOperation:
            exchange_rate = None
        currency = request.POST.get('currency', '').strip()

        # 更新主項目資料
        document.invoice_period = invoice_period
        document.erp_reference = erp_reference
        document.seller_bp_id = seller_bp_id
        document.buyer_bp_id = buyer_bp_id
        document.buyer_remark = buyer_remark
        document.main_remark = main_remark
        document.customs_clearance_mark = customs_clearance_mark
        document.category = category
        document.relate_number = relate_number
        document.bonded_area_confirm = bonded_area_confirm
        document.zero_tax_rate_reason = zero_tax_rate_reason
        document.reserved1 = reserved1
        document.reserved2 = reserved2
        document.original_currency_amount = original_currency_amount
        document.exchange_rate = exchange_rate
        document.currency = currency

        document.save()  # 保存主項目資料

        # 更新明細項目資料
        for item in document.items.all():
            line_remark = request.POST.get(f'line_remark_{item.id}', '').strip()
            line_relate_number = request.POST.get(f'line_relate_number_{item.id}', '').strip()

            item.line_remark = line_remark
            item.line_relate_number = line_relate_number
            item.save()  # 保存明細項目資料

        return redirect('twb2blineitem', id=document.id)  # 更新後重定向到發票詳情頁面

    return render(request, 'document/twb2blineitem.html', {'document': document})


#======================================================B2B發票篩選=======================================================

def twb2bmainitem_filter(request):
    # 預設顯示筆數
    display_limit = int(request.GET.get("display_limit", 20))  # 默認為20筆資料

    # 其他篩選條件
    invoice_status_filter = request.GET.get("invoice_status")
    #void_status_filter = request.GET.get("void_status")
    tax_type_filter = request.GET.get("tax_type")
    company_id_filter = request.GET.get("company_id")  # 新增公司篩選條件


    # 取得登入使用者的 UserProfile
    user_profile = request.user.profile

    # 取得該使用者可查看的公司名稱列表
    company_options = user_profile.viewable_companies.all()
    #viewable_company_codes = user_profile.viewable_companies.values_list('id', flat=True)
    viewable_company_codes = user_profile.viewable_companies.values_list('company_id', flat=True)



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
        return redirect('twb2bmainitem')
    if start_date > end_date:
        messages.error(request, "開始日期不能大於結束日期")
        return redirect('twb2bmainitem')
    
    # 查詢條件構建
    filters = Q()
    if invoice_status_filter:
        filters &= Q(invoice_status=invoice_status_filter)
    
    #if void_status_filter:
    #    filters &= Q(void_status=void_status_filter)
    if tax_type_filter:
        filters &= Q(tax_type=tax_type_filter)
    if company_id_filter:
        filters &= Q(company_id=company_id_filter)

    # 限制在兩個月前到今天的時間範圍內
    filters &= Q(erp_date__range=[start_date, end_date])


    # 加入公司權限過濾條件
    filters &= Q(company__in=viewable_company_codes)

    # 查詢所有符合條件的發票資料
    documents = TWB2BMainItem.objects.filter(filters).order_by('-erp_date')

    for document in documents:
        document.is_disabled = (
            document.invoice_status == '已作廢' or
            (
                document.tax_type == '2' and (
                    (document.zerotax_sales_amount or 0) <= 0 or
                    not document.customs_clearance_mark or
                    not document.bonded_area_confirm or
                    not document.zero_tax_rate_reason
                )
            )
        )


    # 分頁
    paginator = Paginator(documents, display_limit)  # 每頁顯示的資料筆數
    page_number = request.GET.get('page')  # 獲取當前頁碼
    page_obj = paginator.get_page(page_number)  # 根據頁碼獲取相應的頁面資料

    # 獲取篩選條件的選項
    invoice_status = TWB2BMainItem.objects.values_list('invoice_status', flat=True).distinct()
    #void_status = TWB2BMainItem.objects.values_list('void_status', flat=True).distinct()
    tax_type = TWB2BMainItem.objects.values_list('tax_type', flat=True).distinct()

    # 檢查公司ID篩選是否有效
    if company_id_filter and company_id_filter not in viewable_company_codes:
        messages.error(request, "您無權限查看該公司資料")
        return redirect('twb2bmainitem')
    

    return render(request, "twb2bmainitem_filter.html", {
        "company_id_filter": company_id_filter,
        "documents": page_obj,  # 傳遞分頁結果
        "company_options": company_options,
        "invoice_status": invoice_status,
        #"void_status": void_status,
        "tax_type": tax_type,
        "display_limit": display_limit,  # 傳遞選擇的筆數
        "start_date": start_date.strftime('%Y-%m-%d'),  # 顯示篩選的開始日期
        "end_date": end_date.strftime('%Y-%m-%d'),  # 顯示篩選的結束日期
    })

#======================================================B2B發票匯出=======================================================

@csrf_exempt
def twb2bmainitem_export_invoices(request):
    if request.method != 'POST':
        return HttpResponse("Only POST allowed", status=405)

    raw_ids = request.POST.get("selected_documents", "")
    selected_ids = [int(x) for x in raw_ids.split(",") if x.strip().isdigit()]
    if not selected_ids:
        return HttpResponse("No invoice IDs provided", status=400)

    #invoices = TWB2BMainItem.objects.filter(id__in=selected_ids).prefetch_related('items')
    invoices = TWB2BMainItem.objects.filter(id__in=selected_ids).prefetch_related('items').exclude(invoice_status='已開立')

    if not invoices.exists():
        return HttpResponse("No invoices found", status=404)

    # 先找出所有選取的發票
    all_selected_invoices = TWB2BMainItem.objects.filter(id__in=selected_ids)
    # 計算「已開立」的數量
    excluded_count = all_selected_invoices.filter(invoice_status='已開立').count()

    # 篩選出尚未開立的發票
    invoices = all_selected_invoices.exclude(invoice_status='已開立').prefetch_related('items')

    # 如果有被排除的，就提示使用者
    if excluded_count > 0:
        messages.warning(request, f"{excluded_count} 筆已開立的發票已排除，未匯出。")

    # 1️⃣ 統計各公司所需發票數
    #invoice_count_by_company_code = defaultdict(int)
    invoice_count_by_company_id = defaultdict(int)

    for invoice in invoices:
        #invoice_count_by_company_code[invoice.company_id] += 1  # invoice.company_id 是字串
        #invoice_count_by_company_code[invoice.company.company_id] += 1
        invoice_count_by_company_id[invoice.company.company_id] += 1

    # 2️⃣ 建立公司代碼對應的 Company 資料（查主鍵）
    company_map = {
        #company.company_id: company for company in Company.objects.filter(company_id__in=invoice_count_by_company_code.keys())
        company.company_id: company for company in Company.objects.filter(company_id__in=invoice_count_by_company_id.keys())
    
    }

    # 3️⃣ 驗證每間公司是否有足夠的號碼可以使用
    insufficient_companies = []

    #for company_code, count_needed in invoice_count_by_company_code.items():
    for company_id, count_needed in invoice_count_by_company_id.items():
        #company_obj = company_map.get(company_code)
        company_obj = company_map.get(company_id)
        if not company_obj:
            #insufficient_companies.append(f"公司代碼 {company_code} 找不到對應公司資料")
            insufficient_companies.append(f"公司代碼 {company_id} 找不到對應公司資料")
            continue

        distributions = NumberDistribution.objects.filter(
            company=company_obj,
            status='available'
        )

        total_available = sum(
            int(d.end_number) - int(d.current_number or d.start_number) + 1
            for d in distributions
        )

        if total_available < count_needed:
            insufficient_companies.append(f"公司 {company_obj.company_name}（剩 {total_available} 張，需求 {count_needed} 張）")

    if insufficient_companies:
        return HttpResponse("號碼不足，請檢查以下公司：\n" + "\n".join(insufficient_companies), status=400)

    # 4️⃣ 準備號碼池（以 company.id 為 key）
    number_pool = defaultdict(list)
    for dist in NumberDistribution.objects.filter(status='available'):
        #number_pool[dist.company.id].append(dist)
        number_pool[dist.company.company_id].append(dist)

    # 5️⃣ 載入 Excel 樣板
    template_path = os.path.join(settings.BASE_DIR, 'export', 'A0101.xlsx')
    workbook = load_workbook(template_path)
    sheet = workbook.active

    row = 2  # Excel 開始列

    # 6️⃣ 開始配號與寫入 Excel
    with transaction.atomic():
        for invoice in invoices:
            #company_obj = company_map.get(invoice.company_id)
            company_obj = company_map.get(invoice.company.company_id)
            if not company_obj:
                #raise ValueError(f"找不到公司代碼為 {invoice.company_id} 的公司資料")
                raise ValueError(f"找不到公司代碼為 {invoice.company.company_id} 的公司資料")


            distributions = sorted(
                #number_pool[company_obj.id],
                number_pool[company_obj.company_id],
                key=lambda d: int(d.current_number or d.start_number)
            )

            # 找一組號碼配給發票
            assigned = False
            for dist in distributions:
                current = int(dist.current_number or dist.start_number)
                if current <= int(dist.end_number):
                    invoice_number = f"{dist.initial_char}{str(current).zfill(len(dist.start_number))}"
                    invoice.invoice_number = invoice_number
                    invoice.invoice_status = '已開立'
                    invoice.invoice_date = localtime(timezone.now()).replace(tzinfo=None).date()
                    invoice.export_date = localtime(timezone.now()).replace(tzinfo=None).date()
                    invoice.save()

                    dist.current_number = str(current + 1).zfill(len(dist.start_number))
                    dist.last_used_date = timezone.now().date()
                    dist.save()
                    assigned = True
                    break

            if not assigned:
                raise ValueError(f"公司 {company_obj.company_name} 號碼區間不足")

            # 寫入 Excel
            for item in invoice.items.all():
                sheet.cell(row=row, column=1, value=invoice.company.company_id)
                sheet.cell(row=row, column=2, value=invoice.invoice_number)
                sheet.cell(row=row, column=3, value=invoice.invoice_date)
                sheet.cell(row=row, column=4, value=invoice.invoice_time)
                #sheet.cell(row=row, column=5, value=invoice.company.company_name)
                sheet.cell(row=row, column=5, value=invoice.invoice_type)
                sheet.cell(row=row, column=6, value=invoice.company.company_identifier)
                sheet.cell(row=row, column=7, value=invoice.buyer_identifier)
                sheet.cell(row=row, column=8, value=invoice.buyer_name)
                sheet.cell(row=row, column=9, value=invoice.buyer_bp_id)
                sheet.cell(row=row, column=10, value=invoice.buyer_remark)
                sheet.cell(row=row, column=11, value=invoice.main_remark)
                sheet.cell(row=row, column=12, value=invoice.customs_clearance_mark)
                sheet.cell(row=row, column=13, value=invoice.category)
                sheet.cell(row=row, column=14, value=invoice.relate_number)
                sheet.cell(row=row, column=15, value=invoice.bonded_area_confirm)
                sheet.cell(row=row, column=16, value=invoice.zero_tax_rate_reason)
                sheet.cell(row=row, column=17, value=invoice.reserved1)
                sheet.cell(row=row, column=18, value=invoice.reserved2)
                sheet.cell(row=row, column=19, value=invoice.sales_amount)
                sheet.cell(row=row, column=20, value=invoice.freetax_sales_amount)
                sheet.cell(row=row, column=21, value=invoice.zerotax_sales_amount)
                sheet.cell(row=row, column=22, value=invoice.tax_type)
                sheet.cell(row=row, column=23, value=invoice.tax_rate)
                sheet.cell(row=row, column=24, value=float(invoice.total_tax_amount))
                sheet.cell(row=row, column=25, value=float(invoice.total_amount))
                sheet.cell(row=row, column=26, value=invoice.original_currency_amount)
                sheet.cell(row=row, column=27, value=invoice.exchange_rate)
                sheet.cell(row=row, column=28, value=invoice.currency)
                sheet.cell(row=row, column=29, value=item.line_description)
                sheet.cell(row=row, column=30, value=item.line_quantity)
                sheet.cell(row=row, column=31, value=item.line_unit)
                sheet.cell(row=row, column=32, value=float(item.line_unit_price))
                sheet.cell(row=row, column=33, value=item.line_tax_type)
                sheet.cell(row=row, column=34, value=float(item.line_amount))
                sheet.cell(row=row, column=35, value=item.line_sequence_number)
                sheet.cell(row=row, column=36, value=item.line_remark)
                sheet.cell(row=row, column=37, value=item.line_relate_number)
                row += 1

    # 匯出 Excel
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="invoices.xlsx"'
    return response


@csrf_exempt
def twb2bmainitem_delete_selected_invoices(request):
    if request.method == 'POST':
        selected_ids_raw = request.POST.get('selected_documents', '')
        selected_ids = selected_ids_raw.split(',') if selected_ids_raw else []

        if not selected_ids:
            messages.error(request, "刪除失敗：未選擇任何發票。")
            return redirect('twb2bmain')

        # 只刪除 invoice_status 為「未開立」的發票
        invoices_to_delete = TWB2BMainItem.objects.filter(id__in=selected_ids, invoice_status="未開立")
        deleted_count, _ = invoices_to_delete.delete()

        if deleted_count > 0:
            messages.success(request, f"成功刪除 {deleted_count} 筆發票。")
        else:
            messages.warning(request, "未找到對應的發票資料，未進行刪除。")

        return redirect('twb2bmainitem')
    else:
        return redirect('twb2bmainitem')
        
@csrf_exempt
def twb2bmainitem_update_void_status(request):
    if request.method != 'POST':
        return HttpResponse("Only POST allowed", status=405)

    raw_ids = request.POST.get("selected_documents", "")
    selected_ids = [int(x) for x in raw_ids.split(",") if x.strip().isdigit()]
    if not selected_ids:
        return HttpResponse("No invoice IDs provided", status=400)

    invoices = TWB2BMainItem.objects.filter(id__in=selected_ids).prefetch_related('items')
    if not invoices.exists():
        return HttpResponse("No invoices found", status=404)

    # 載入 Excel 樣板
    template_path = os.path.join(settings.BASE_DIR, 'export', 'A0201.xlsx')
    workbook = load_workbook(template_path)
    sheet = workbook.active

    row = 2  # Excel 開始列

    with transaction.atomic():
        for invoice in invoices:
            # 更新作廢狀態與時間
            invoice.invoice_status = '已作廢'
            invoice.cancel_date = localtime(timezone.now()).replace(tzinfo=None).date()
            invoice.cancel_time = localtime(timezone.now()).replace(tzinfo=None).time()
            invoice.original_invoice_date = invoice.invoice_date
            invoice.original_invoice_number = invoice.invoice_number
            invoice.save()


            sheet.cell(row=row, column=1, value=invoice.company.company_identifier)
            sheet.cell(row=row, column=2, value=invoice.buyer_identifier)
            sheet.cell(row=row, column=3, value=invoice.invoice_date)
            sheet.cell(row=row, column=4, value=invoice.invoice_number)
            sheet.cell(row=row, column=5, value=invoice.invoice_period)
            sheet.cell(row=row, column=6, value=invoice.cancel_date)
            sheet.cell(row=row, column=7, value=invoice.cancel_time)
            sheet.cell(row=row, column=8, value=invoice.cancel_period)
            sheet.cell(row=row, column=9, value=invoice.cancel_reason)
            sheet.cell(row=row, column=10, value=invoice.returntax_document_number)
            sheet.cell(row=row, column=11, value=invoice.cancel_remark)
            row += 1

    # 匯出 Excel
    output = BytesIO()
    workbook.save(output)
    output.seek(0)

    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="void.xlsx"'
    return response