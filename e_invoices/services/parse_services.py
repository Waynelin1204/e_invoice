
import pandas as pd
from e_invoices.models.twb2bmainitem_models import TWB2BMainItem, TWB2BLineItem
from e_invoices.models.twallowance_models import TWAllowance, TWAllowanceLineItem
from e_invoices.views.company_views import validateUniformNumberTW
from e_invoices.models.uploadlog_models import UploadLog
from e_invoices.models.company_models import Company
from django.db import transaction
from datetime import datetime
import os
import math
from pandas._libs.tslibs.nattype import NaTType    
from collections import defaultdict

def safe_datetime(value):
    if isinstance(value, datetime):
        return value
    elif isinstance(value, (str, float)) and pd.notna(value):
        try:
            return pd.to_datetime(value)
        except Exception:
            return None
    elif isinstance(value, NaTType) or pd.isna(value):
        return None
    return None

def safe_float(value):
    try:
        f = float(value)
        return 0.0 if math.isnan(f) else f
    except Exception:
        return 0.0

def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


REQUIRED_COLUMNS = [
    "erp_number", "erp_date", "erp_reference", "seller_bp_id", "buyer_identifier",
    "buyer_name", "buyer_bp_id", "buyer_remark", "main_remark", "customs_clearance_mark",
    "category", "relate_number", "bonded_area_confirm", "zero_tax_rate_reason",
    "sales_amount", "zerotax_sales_amount", "freetax_sales_amount",
    "tax_type", "total_tax_amount", "total_amount"
]


def validate_row(row, company_id, line_grouped_dict=None):
    errors = []

    # === E01: 必填欄位不可為空 ===
    required_main_fields = [
        "invoice_period", "erp_number", "erp_date", "buyer_identifier", "buyer_name",
        "sales_amount", "zerotax_sales_amount", "freetax_sales_amount",
        "tax_type", "total_tax_amount", "total_amount"
    ]
    required_line_fields = [
        "line_sequence_number", "line_description", "line_quantity",
        "line_unit", "line_unit_price", "line_tax_type", "line_amount"
    ]
    required_fields = required_main_fields + required_line_fields

    missing_fields = [
        field for field in required_fields
        if pd.isna(row.get(field)) or str(row.get(field)).strip() == ""
    ]
    if missing_fields:
        errors.append(f"E01-必填欄位不可為空：{', '.join(missing_fields)}")

    # === E02: 格式錯誤或無效 ===
    format_error_fields = []

    buyer_identifier = str(row.get("buyer_identifier")).strip()
    if buyer_identifier and not validateUniformNumberTW(buyer_identifier):
        format_error_fields.append("buyer_identifier")

    if format_error_fields:
        errors.append(f"E02-格式錯誤或無效：{', '.join(format_error_fields)}")

    # === E03: 資料重複 ===
    sys_number = row.get("sys_number")
    if sys_number and TWB2BMainItem.objects.filter(sys_number=sys_number).exists():
        errors.append("E03-資料重複：此筆資料已存在")

    # === E04: 金額完整性 ===
    if line_grouped_dict:
        erp_number = str(row.get("erp_number"))

        # 1. sales_amount 應稅合計
        expected_sales = line_grouped_dict.get((erp_number, 1), 0.0)
        if abs(float(row.get("sales_amount", 0)) - expected_sales) >= 1:
            errors.append("E04-金額完整性：應稅銷售額明細加總不一致")

        # 2. zerotax_sales_amount 零稅率合計
        expected_zerotax = line_grouped_dict.get((erp_number, 2), 0.0)
        if abs(float(row.get("zerotax_sales_amount", 0)) - expected_zerotax) >= 1:
            errors.append("E04-金額完整性：零稅率銷售額明細加總不一致")

        # 3. freetax_sales_amount 免稅合計
        expected_freetax = line_grouped_dict.get((erp_number, 3), 0.0)
        if abs(float(row.get("freetax_sales_amount", 0)) - expected_freetax) >= 1:
            errors.append("E04-金額完整性：免稅銷售額明細加總不一致")

        # 4. 營業稅 total_tax_amount 應接近 sales_amount * 5%
        sales_amount = float(row.get("sales_amount", 0))
        total_tax_amount = float(row.get("total_tax_amount", 0))
        if sales_amount > 0:
            expected_tax = sales_amount * 0.05
            if abs(total_tax_amount - expected_tax) >= 1:
                errors.append("E04-金額完整性：營業稅 total_tax_amount 誤差過大")

    return errors


def allowance_validate_row(row, company_id, allowance_amount_dict, allowance_tax_dict, invoice_status_map, original_invoice_dict):
    errors = []
    
    # === E01: 必填欄位不可為空 ===
    required_main_fields = [
        "allowance_period","erp_number", "erp_date", "buyer_identifier", "buyer_name",
        "total_allowance_amount", "total_allowance_tax"
    ]
    required_line_fields = [
        "line_sequence_number", "line_description", "line_quantity",
        "line_unit", "line_unit_price", "line_tax_type", "line_allowance_amount", "line_allowance_tax",
        "line_original_invoice_date", "line_original_invoice_number"
    ]
    required_fields = required_main_fields + required_line_fields

    missing_fields = [
        field for field in required_fields
        if pd.isna(row.get(field)) or str(row.get(field)).strip() == ""
    ]
    if missing_fields:
        errors.append(f"E01-必填欄位不可為空：{', '.join(missing_fields)}")
    
    # === E02: 格式錯誤或無效 ===
    format_error_fields = []

    buyer_identifier = str(row.get("buyer_identifier")).strip()
    
    if buyer_identifier and not validateUniformNumberTW(buyer_identifier):
        format_error_fields.append("buyer_identifier")
    
    if format_error_fields:
        errors.append(f"E02-格式錯誤或無效：{', '.join(format_error_fields)}")
    
        # === E03: 資料重複 ===
    sys_number = row.get("sys_number")
    if sys_number and TWAllowance.objects.filter(sys_number=sys_number).exists():
        errors.append("E03-資料重複：此筆資料已存在")
        # === E04: 金額完整性 ===

    if allowance_amount_dict:
        erp_number = str(row.get("erp_number"))
        expected_amount = allowance_amount_dict.get(erp_number, 0.0)
        if abs(float(row.get("total_allowance_amount", 0)) - expected_amount) >= 1:
            errors.append("E04-金額完整性：折讓金額明細加總不一致")


    if allowance_tax_dict:
        erp_number = str(row.get("erp_number"))
        expected_tax = allowance_tax_dict.get(erp_number,0.0)
        if abs(float(row.get("total_allowance_tax", 0)) - expected_tax) >= 1:
            errors.append("E04-金額完整性：折讓稅額明細加總不一致")

        # # 4. 營業稅 total_tax_amount 應接近 sales_amount * 5%
        # total_allowance_amount = float(row.get("total_allowance_amount", 0))
        # total_allowance_tax = float(row.get("total_allowance_tax", 0))
        # if total_allowance_amount > 0:
        #     expected_tax = total_allowance_amount * 0.05
        #     if abs(total_allowance_tax - expected_tax) >= 1:
        #         errors.append("E04-金額完整性：營業稅 total_allowance_tax 誤差過大")
        
    line_original_invoice_number = str(row.get("line_original_invoice_number")).strip()
    seq_num = safe_int(row.get("line_sequence_number"))
    current_description = str(row.get("line_description")).strip()
    print(line_original_invoice_number)
    print(current_description)

    if line_original_invoice_number:
        status = invoice_status_map.get(line_original_invoice_number)

        if not status:
            errors.append(f"E05-原發票號碼 {line_original_invoice_number} 查無發票資料")
        elif status != "已開立":
            errors.append(f"E05-原發票號碼 {line_original_invoice_number} 為「{status}」，不允許折讓")
        else:
            linked_invoice = TWB2BMainItem.objects.filter(
                invoice_number=line_original_invoice_number
            ).prefetch_related('items').first()
            print(linked_invoice)

            if linked_invoice:
                original_descriptions = [
                    (item.line_description or "").strip()
                    for item in linked_invoice.items.all()
                ]

                if current_description not in original_descriptions:
                    errors.append(
                        f"E06-折讓品名「{current_description}」在原發票中找不到對應品名"
                    )

    return errors




def process_data(file_path, company_id, b2b_b2c, import_type, username):
    print(f"[process_data] file_path={file_path}, company_id={company_id}, b2b_b2c={b2b_b2c}, import_type={import_type}, username={username}")
    
    # 讀檔案
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # 查公司資料
    company_obj = Company.objects.get(company_id=company_id)
    company_identifier = company_obj.company_identifier
    c_id = company_obj.company_id
    tax_identifier = company_obj.tax_identifier
    seller_name = company_obj.company_name

    if import_type == "invoice":
        # line_amount 分組加總（for E04金額完整性）
        line_grouped = df.groupby(["erp_number", "line_tax_type"])["line_amount"].sum().reset_index()
        line_grouped_dict = {
            (str(row["erp_number"]), int(row["line_tax_type"])): float(row["line_amount"])
            for _, row in line_grouped.iterrows()
        }
    elif import_type == "allowance":
    # allowance line_amount 分組加總（for E04金額完整性）
        df["erp_number"] = df["erp_number"].astype(str)
        amount_grouped = df.fillna({"line_allowance_amount": 0}).groupby("erp_number")["line_allowance_amount"].sum().reset_index()
        allowance_amount_dict = {
            str(row["erp_number"]): float(row["line_allowance_amount"])
            for _, row in amount_grouped.iterrows()
        }
       
        # 稅額加總
        #tax_grouped = df.groupby(["erp_number"])["line_allowance_tax"].sum().reset_index()
        df["erp_number"] = df["erp_number"].astype(str)
        tax_grouped = df.fillna({"line_allowance_tax": 0}).groupby("erp_number")["line_allowance_tax"].sum().reset_index()
        allowance_tax_dict = {
            str(row["erp_number"]): float(row["line_allowance_tax"])
            for _, row in tax_grouped.iterrows()
        }

        # === 建立 erp_number -> 所有原發票號碼的 dict ===
        original_invoice_dict = df["line_original_invoice_number"].fillna("").astype(str)
        original_invoice_dict = (
            df.groupby("erp_number")["line_original_invoice_number"]
            .apply(lambda x: list(x.dropna().astype(str)))
            .to_dict()
        )

        # === Step: 查詢所有原發票號碼的狀態，避免 N+1 ===
        all_original_invoices = set(i for sublist in original_invoice_dict.values() for i in sublist if i)
        invoice_qs = TWB2BMainItem.objects.filter(invoice_number__in=all_original_invoices)
        invoice_status_map = {
            i.invoice_number: i.invoice_status
            for i in invoice_qs
        }
        #print(invoice_qs)
        #print(invoice_status_map)

    valid_rows = []
    error_rows = []
    grouped_rows = defaultdict(list)
    # 清理資料並驗證
    # 先清理＆分組資料
    for _, row in df.iterrows():
        cleaned_row = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
        cleaned_row["erp_date"] = safe_datetime(cleaned_row.get("erp_date"))
        erp_number = str(cleaned_row.get("erp_number")).strip()
        erp_date_str = cleaned_row["erp_date"].strftime("%Y%m%d") if cleaned_row["erp_date"] else ""
        cleaned_row["sys_number"] = f"{company_id}{erp_date_str}{erp_number}"
        cleaned_row["company_identifier"] = company_identifier
        cleaned_row["tax_rate"] = 0.05 if safe_int(cleaned_row.get("tax_type")) == 1 else 0
        grouped_rows[erp_number].append(cleaned_row)

    # 再根據類型驗證整組
    for erp_number, group in grouped_rows.items():
        if import_type == "invoice":
            for row in group:
                error_list = validate_row(row, company_id, line_grouped_dict)
                if error_list:
                    row["errors"] = "; ".join(error_list)
                    error_rows.append(row)
                else:
                    valid_rows.append(row)

        elif import_type == "allowance":
            group_has_errors = False
            for row in group:
                allowance_error_list = allowance_validate_row(
                    row, company_id,
                    allowance_amount_dict,
                    allowance_tax_dict,
                    invoice_status_map,
                    original_invoice_dict
                )
                if allowance_error_list:
                    group_has_errors = True
                    row["errors"] = "; ".join(allowance_error_list)
            if group_has_errors:
                error_rows.extend(group)
            else:
                valid_rows.extend(group)


            #驗證allowance
            # allowance_error_list = allowance_validate_row(cleaned_row, company_id, allowance_amount_dict, allowance_tax_dict, invoice_status_map, original_invoice_dict)
            # if allowance_error_list:
            #     cleaned_row["errors"] = "; ".join(allowance_error_list)
            #     error_rows.append(cleaned_row)
            #     print(error_rows)
            # else:
            #     valid_rows.append(cleaned_row)
            #     print(valid_rows)

    

    

    # 如果有錯誤，產生錯誤Excel
    error_excel_path = None
    if error_rows:
        error_excel_path = save_error_excel(error_rows, file_path)

    # 把 valid_rows 寫入DB
    with transaction.atomic():
        main_item_cache = {}
        for row in valid_rows:
            if import_type == "invoice":
                sys_number = row["sys_number"]

                if sys_number in main_item_cache:
                    main_item = main_item_cache[sys_number]
                else:
                    
                    main_item, created = TWB2BMainItem.objects.get_or_create(
                        sys_number=sys_number,
                        defaults={
                            "company_id": c_id,
                            "b2b_b2c": b2b_b2c,
                            "sys_date": datetime.now(),
                            "invoice_period": row.get("invoice_period"),
                            "invoice_type": '07',
                            "invoice_number": '',
                            "erp_number": row.get("erp_number"),
                            "erp_date": row.get("erp_date"),
                            "erp_reference": row.get("erp_reference"),
                            "company_identifier": company_identifier,
                            "seller_bp_id": row.get("seller_bp_id"),
                            "tax_identifier": tax_identifier,
                            "seller_name": seller_name,
                            "buyer_identifier": row.get("buyer_identifier"),
                            "buyer_name": row.get("buyer_name"),
                            "buyer_bp_id": row.get("buyer_bp_id"),
                            "buyer_remark": row.get("buyer_remark"),
                            "main_remark": row.get("main_remark"),
                            "customs_clearance_mark": row.get("customs_clearance_mark"),
                            "category": row.get("category"),
                            "relate_number": row.get("relate_number"),
                            "bonded_area_confirm": row.get("bonded_area_confirm"),
                            "zero_tax_rate_reason": row.get("zero_tax_rate_reason"),
                            "sales_amount": safe_float(row.get("sales_amount")),
                            "freetax_sales_amount": safe_float(row.get("freetax_sales_amount")),
                            "zerotax_sales_amount": safe_float(row.get("zerotax_sales_amount")),
                            "tax_type": safe_int(row.get("tax_type")),
                            "tax_rate": safe_float(row.get("tax_rate")),
                            "total_tax_amount": safe_float(row.get("total_tax_amount")),
                            "total_amount": safe_float(row.get("total_amount")),
                            "original_currency_amount": safe_float(row.get("original_currency_amount")),
                            "exchange_rate": safe_float(row.get("exchange_rate")),
                            "currency": row.get("currency"),
                            "creator": username,
                        }
                    )
                    main_item_cache[sys_number] = main_item

                # 建立 LineItem
                TWB2BLineItem.objects.create(
                    twb2bmainitem_id=main_item.id,
                    line_description=row.get("line_description"),
                    line_amount=safe_float(row.get("line_amount")),
                    line_tax_amount=safe_float(row.get("line_tax_amount")),
                    line_tax_type=safe_int(row.get("line_tax_type")),
                    line_quantity=row.get("line_quantity"),
                    line_unit=row.get("line_unit"),
                    line_unit_price=safe_float(row.get("line_unit_price")),
                    line_sequence_number=safe_int(row.get("line_sequence_number")),
                    line_relate_number=row.get("line_relate_number")
                )

            elif import_type == "allowance":
                sys_number = row["sys_number"]

                if sys_number in main_item_cache:
                    main_item = main_item_cache[sys_number]
                else:
                    main_item, created = TWAllowance.objects.get_or_create(
                        sys_number=sys_number,
                        defaults={
                            "company_id": c_id,
                            "b2b_b2c": b2b_b2c,
                            "sys_date": datetime.now(),
                            "allowance_period": row.get("allowance_period"),
                            "allowance_type": '2',
                            "allowance_number": row.get("allowance_number"),
                            "erp_number": row.get("erp_number"),
                            "erp_date": row.get("erp_date"),
                            "erp_reference": row.get("erp_reference"),
                            #"company_identifier": company_identifier,
                            "seller_bp_id": row.get("seller_bp_id"),
                            #"tax_identifier": tax_identifier,
                            #"seller_name": seller_name,
                            "buyer_identifier": row.get("buyer_identifier"),
                            "buyer_name": row.get("buyer_name"),
                            "buyer_bp_id": row.get("buyer_bp_id"),
                            #"buyer_remark": row.get("buyer_remark"),
                            #"main_remark": row.get("main_remark"),
                            #"customs_clearance_mark": row.get("customs_clearance_mark"),
                            #"category": row.get("category"),
                            #"relate_number": row.get("relate_number"),
                            #"bonded_area_confirm": row.get("bonded_area_confirm"),
                            #"zero_tax_rate_reason": row.get("zero_tax_rate_reason"),
                            #"sales_amount": safe_float(row.get("sales_amount")),
                            #"freetax_sales_amount": safe_float(row.get("freetax_sales_amount")),
                            #"zerotax_sales_amount": safe_float(row.get("zerotax_sales_amount")),
                            #"tax_type": safe_int(row.get("tax_type")),
                            #"tax_rate": safe_float(row.get("tax_rate")),
                            #"total_tax_amount": safe_float(row.get("total_tax_amount")),
                            #"total_amount": safe_float(row.get("total_amount")),
                            #"original_currency_amount": safe_float(row.get("original_currency_amount")),
                            #"exchange_rate": safe_float(row.get("exchange_rate")),
                            #"currency": row.get("currency"),
                            "allowance_amount": safe_float(row.get("total_allowance_amount")),
                            "allowance_tax": safe_float(row.get("total_allowance_tax")),
                            "allowance_status": '未開立',
                            #"creator": username,
                        }
                    )
                    main_item_cache[sys_number] = main_item

                # line_original_invoice_number = row.get("line_original_invoice_number")
                #     # 預設取消狀態
                # line_invoice_cancel_status = ""

                # if line_original_invoice_number:
                #     try:
                #         linked_invoice = TWB2BMainItem.objects.get(invoice_number=line_original_invoice_number, company_id=c_id)
                #         if linked_invoice.invoice_status == "已作廢":
                #             line_invoice_cancel_status = "無效"
                #         else:
                #             line_invoice_cancel_status = "有效"
                #     except TWB2BMainItem.DoesNotExist:
                #         line_invoice_cancel_status = "找不到原發票"
                # else:
                #     line_invoice_cancel_status = "無原發票號碼"


                # 建立 LineItem
                # TWAllowanceLineItem.objects.create(
                #     twallowance_id=main_item.id,
                #     line_description=row.get("line_description"),
                #     line_allowance_amount=safe_float(row.get("line_allowance_amount")),
                #     line_allowance_tax=safe_float(row.get("line_allowance_tax")),
                #     line_tax_type=safe_int(row.get("line_tax_type")),
                #     line_quantity=row.get("line_quantity"),
                #     line_unit=row.get("line_unit"),
                #     line_unit_price=safe_float(row.get("line_unit_price")),
                #     line_sequence_number=safe_int(row.get("line_sequence_number")),
                #     #line_relate_number=row.get("line_relate_number"),
                #     line_original_invoice_date=row.get("line_original_invoice_date"),
                #     line_original_invoice_number=row.get("line_original_invoice_number"),
                #     #line_invoice_cancel_status=line_invoice_cancel_status,
                # )

                #是的，我們仍然在寫入資料。只是換了一種方式 —— 先建立一個物件（不儲存），補上 linked_invoice 關聯，再 save() 寫入。
                # 建立 LineItem
                allowance_line = TWAllowanceLineItem(
                    twallowance_id=main_item.id,
                    line_description=row.get("line_description"),
                    line_allowance_amount=safe_float(row.get("line_allowance_amount")),
                    line_allowance_tax=safe_float(row.get("line_allowance_tax")),
                    line_tax_type=safe_int(row.get("line_tax_type")),
                    line_quantity=row.get("line_quantity"),
                    line_unit=row.get("line_unit"),
                    line_unit_price=safe_float(row.get("line_unit_price")),
                    line_sequence_number=safe_int(row.get("line_sequence_number")),
                    line_original_invoice_date=row.get("line_original_invoice_date"),
                    line_original_invoice_number=row.get("line_original_invoice_number"),
                )

                # 查找對應的原發票（若存在則關聯）
                line_original_invoice_number = row.get("line_original_invoice_number")
                if line_original_invoice_number:
                    linked_invoice = TWB2BMainItem.objects.filter(
                        invoice_number=line_original_invoice_number, company_id=c_id
                    ).first()
                    if linked_invoice:
                        allowance_line.linked_invoice = linked_invoice

                # 儲存
                allowance_line.save()

    # Log寫入
    success_count = len(valid_rows)
    error_count = len(error_rows)

    UploadLog.objects.create(
        company_id=company_id,
        import_type=import_type,
        business_type=b2b_b2c,
        file_name=os.path.basename(file_path),
        success_count=success_count,
        error_count=error_count,
        error_excel_path=error_excel_path,  # 這裡是 '/upload/xxx_error.xlsx'
        upload_user=username,
        upload_time=datetime.now()
    )

    return {
        "success": len(error_rows) == 0,
        "error_excel_path": error_excel_path,
        "error_count": error_count,
        "success_count": success_count,
    }


def save_error_excel(error_rows, original_file_path):
    if not error_rows:
        return None

    # 取原本上傳檔案的資料欄位
    original_columns = [col for col in error_rows[0].keys() if col != 'errors']

    # 新的欄位順序：先放 "errors"，再放其他欄位
    columns = ['errors'] + original_columns

    # 依照順序建 DataFrame
    error_df = pd.DataFrame(error_rows)[columns]

    # 設定儲存路徑
    base_dir = os.path.dirname(original_file_path)
    filename = os.path.basename(original_file_path)

    if filename.endswith('.xlsx'):
        filename = filename.replace('.xlsx', '_error.xlsx')
    elif filename.endswith('.xls'):
        filename = filename.replace('.xls', '_error.xlsx')
    elif filename.endswith('.csv'):
        filename = filename.replace('.csv', '_error.xlsx')
    else:
        filename = filename + '_error.xlsx'  # 如果副檔名很奇怪就直接加

    error_path = os.path.join(base_dir, filename)

    # 儲存錯誤檔案
    error_df.to_excel(error_path, index=False)

    # ⚡️重點：回傳的是錯誤檔的相對網址路徑（給html用）
    error_web_path = os.path.join('/upload/', filename).replace('\\', '/')
    return error_web_path
