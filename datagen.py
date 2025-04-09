from decimal import Decimal
from django.utils import timezone
from e_invoices.models import Twa0101, Twa0101Item
import random

seller_names = ["公司A", "公司B", "公司C", "公司D"]
buyer_names = ["公司E", "公司F", "公司G", "公司D"]
product_names = ["商品X", "商品Y", "商品Z", "商品W", "商品V", "商品U"]

data_list = []
items_list = []

relate_number_counter = 1  # relate_number 初始值


for i in range(100):  # 修改為 100 筆
    tax_type = random.choice(["1", "2", "3", "4", "9"])
    
    if tax_type == "2":
        customs_clearance_mark = random.choice(["1", "2"])
        zero_tax_rate_reason = "出口免稅"
    else:
        customs_clearance_mark = None
        zero_tax_rate_reason = None
    
    relate_number = F"INV{str(i+1).zfill(5)}"

    invoice = Twa0101(
        data_type=random.choice(["H1", "H2", "H3"]),
        job_type=random.choice(["H", "G"]),
        corporate_id=f"{random.randint(10000000, 99999999)}",
        invoice_number="",
        invoice_date=timezone.now().date(),
        invoice_time=timezone.now().time(),
        seller_name=random.choice(seller_names),
        buyer_name=random.choice(buyer_names),
        buyer_remark=None,
        main_remark=None,
        customs_clearance_mark=customs_clearance_mark,
        category=None,
        relate_number=relate_number,
        invoice_type=random.choice(["二聯式", "三聯式", "特種"]),
        group_mark=random.choice(["Y", "N", None]),
        donate_mark=random.choice(["1", "0"]),
        zero_tax_rate_reason=zero_tax_rate_reason,
        reserved1="",
        reserved2="",
        description=f"商品{random.randint(1, 100)}",
        quantity=None,
        unit="",
        unit_price=None,
        tax_type=tax_type,
        amount=Decimal(random.uniform(100, 50000)).quantize(Decimal(".0000001")),
        sequence_number=f"{i+1:04d}",
        remark="單一備註" if random.random() > 0.5 else "",
        sales_amount=Decimal(random.randint(1000, 50000)),
        tax_rate=random.choice(["0.05", "0", None]),
        tax_amount=Decimal(random.randint(50, 5000)),
        total_amount=Decimal(random.randint(1000, 55000)),
        discount_amount=Decimal(random.randint(0, 5000)) if random.random() > 0.5 else None,
        original_currency_amount=Decimal(random.uniform(100, 50000)).quantize(Decimal(".0000001")) if random.random() > 0.5 else None,
        exchange_rate=Decimal(random.uniform(28, 32)).quantize(Decimal(".00001")) if random.random() > 0.5 else None,
        currency=random.choice(["TWD", "USD", "EUR", None]),
        payment_status=random.choice(["已付款", "未付款", None]),
        status=random.choice(["有效", "作廢", "待確認"]),
        invoice_status="未開立",
        void_status="未作廢",
    )
    data_list.append(invoice)

Twa0101.objects.bulk_create(data_list)

for invoice in Twa0101.objects.all():
    for j in range(4):  # 每張發票有 4 個商品項目
        item = Twa0101Item(
            twa0101=invoice,
            product_name=random.choice(product_names),
            quantity=str(random.randint(1, 10)),
            unit=random.choice(["個", "箱", "公斤", None]),
            unit_price=Decimal(random.uniform(10, 5000)).quantize(Decimal(".0000001")),
            amount=Decimal(random.uniform(100, 5000)).quantize(Decimal(".0000001")),
            remark="商品備註" if random.random() > 0.5 else "",
            sequence_number=f"{j+1:04d}"
        )
        items_list.append(item)

Twa0101Item.objects.bulk_create(items_list)
print("已成功插入 100 筆發票，每張發票 4 個商品項目！")
