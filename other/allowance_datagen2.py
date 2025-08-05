from decimal import Decimal
from django.utils import timezone
from e_invoices.models import TWAllowance, TWAllowanceLineItem, Company
from datetime import datetime

data = [
    # company_code, allowance_number, allowance_date, allowance_time, allowance_type, company_identifier, buyer_identifier, buyer_name,
    # line_sequence_number, line_original_number, line_original_invoice_date, description, quantity, unit, unit_price, tax_type, line_allowance_amount, line_allowance_tax, total_amount, total_tax
    ("TW25", "TA20250422001", "2025-04-22", "03:26:11", "02", "12586644", "7777", "公司F", "0001", "AE00000023", "2025-04-21", "商品W", 10, "個", 2010.5120000, "1", 20105.1200000, 0, 194169.579, 0),
    ("TW25", "TA20250422001", "2025-04-22", "03:26:11", "02", "12586644", "6666", "公司G", "0002", "AE00000022", "2025-04-21", "商品Z", 8, "個", 4715.668, "3", 37725.344, 0, 194169.579, 0),
    ("TW25", "TA20250422001", "2025-04-22", "03:26:11", "02", "12586644", "6666", "公司G", "0003", "AE00000022", "2025-04-21", "商品U", 8, "個", 4074.275, "3", 32594.2, 0, 194169.579, 0),
    ("TW25", "TA20250422001", "2025-04-22", "03:26:11", "02", "12586644", "6666", "公司G", "0004", "AE00000022", "2025-04-21", "商品W", 7, "箱", 2302.728, "1", 16119.096, 0, 194169.579, 0),
    ("TW25", "TA20250422001", "2025-04-22", "03:26:11", "02", "12586644", "6666", "公司G", "0001", "AE00000024", "2025-04-21", "商品W", 10, "個", 4119.138, "2", 41191.38, 0, 57700.9970000, 2885),
    ("TW25", "TA20250422001", "2025-04-22", "03:26:11", "02", "12586644", "6666", "公司G", "0002", "AE00000024", "2025-04-21", "商品X", 6, "個", 330.779, "2", 1984.674, 0, 57700.9970000, 2885),
    ("TW25", "TA20250422001", "2025-04-22", "03:26:11", "02", "12586644", "6666", "公司G", "0003", "AE00000024", "2025-04-21", "商品U", 9, "個", 3551.216, "2", 31960.944, 0, 57700.9970000, 2885),
    ("TW25", "TA20250422001", "2025-04-22", "03:26:11", "02", "12586644", "6666", "公司G", "0004", "AE00000024", "2025-04-21", "商品W", 6, "箱", 3576.823, "2", 21460.938, 0, 57700.9970000, 2885),
]

grouped = {}
for row in data:
    key = (row[1], row[4], row[5], row[6], row[7])  # allowance_number, allowance_type, seller_id, buyer_id, buyer_name, erp_number
    grouped.setdefault(key, []).append(row)

for (allowance_number, allowance_type, seller_id, buyer_id, buyer_name), lines in grouped.items():
    company = Company.objects.filter(company_identifier=seller_id).first()
    if not company:
        print(f"❌ 找不到 seller: {seller_id}")
        continue

    # 基本資料統一
    row = lines[0]
    company_code = row[0]
    allowance_date = datetime.strptime(row[2], "%Y-%m-%d").date()
    allowance_time = datetime.strptime(row[3], "%H:%M:%S").time()
    erp_date = datetime.strptime(row[10], "%Y-%m-%d")

    allowance = TWAllowance.objects.create(
        company=company,
        company_code=company_code,
        b2b_b2c="B2B",
        sys_number=f"{company_code}{allowance_number}",
        sys_date=timezone.now(),
        allowance_number=allowance_number,
        allowance_date=allowance_date,
        allowance_type=allowance_type,
        erp_date=erp_date,
        buyer_identifier=buyer_id,
        buyer_name=buyer_name,
        allowance_amount=Decimal("0"),
        allowance_tax=Decimal("0"),
        allowance_status="未開立"
    )

    total_amount = Decimal("0")
    total_tax = Decimal("0")

    for row in lines:
        line_amount = Decimal(row[17])
        line_tax = Decimal(row[18])
        total_amount += line_amount
        total_tax += line_tax

        TWAllowanceLineItem.objects.create(
            twallowance=allowance,
            line_sequence_number=row[8],
            line_original_invoice_number=row[9],
            line_original_invoice_date=datetime.strptime(row[10], "%Y-%m-%d").date(),
            line_description=row[11],
            line_quantity=Decimal(row[12]),
            line_unit=row[13],
            line_unit_price=Decimal(row[14]),
            line_tax_type=row[15],
            line_allowance_amount=line_amount,
            line_allowance_tax=line_tax,
        )

    allowance.allowance_amount = total_amount
    allowance.allowance_tax = total_tax
    allowance.save()

print("✅ 已成功寫入折讓單資料！")
