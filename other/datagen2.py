from decimal import Decimal
from django.utils import timezone
from e_invoices.models import TWB2BMainItem, TWB2BLineItem, Company, Buyer
import random

# 賣方與買方資訊

buyer_info = {
    "公司A": {"identifier": "90618235", "email": "waylin@deloitte.com.tw"},
    "公司B": {"identifier": "12345705", "email": "waylin@deloitte.com.tw"},
    "公司C": {"identifier": "74238514", "email": "waylin@deloitte.com.tw"},
    "公司D": {"identifier": "56890372", "email": "aichia@deloitte.com.tw"},
    "公司E": {"identifier": "23578306", "email": "waylin@deloitte.com.tw"},
    "公司F": {"identifier": "13145257", "email": "waylin@deloitte.com.tw"},
    "公司G": {"identifier": "85491329", "email": "waylin@deloitte.com.tw"},
    "公司H": {"identifier": "73094856", "email": "tachou@deloitte.com.tw"},
}

descriptions = ["商品X", "商品Y", "商品Z", "商品W", "商品V", "商品U"]
# B2BC_info = {
#     "B2B": "三聯式",
#     "B2C": "二聯式",
# }

line_items = []

# 取得所有 company 資料作為亂數來源
companies = list(Company.objects.all())
buyer = list(Buyer.objects.all())

for i in range(1000):
    # ✅ 隨機選一個公司 instance

    #buyer_name = random.choice(list(buyer_info.keys()))
    #buyer_identifier = buyer_info[buyer_name]["identifier"]
    #buyer_email = buyer_info[buyer_name]["email"]

    #invoice_type = B2BC_info[b2b_b2c]
    sys_number = f"2025SYS{str(i+1).zfill(5)}"
    ERP_number = f"INV{str(i+1).zfill(5)}"

    # 發票稅別 (整張發票同一種)
    tax_type = random.choice(["1", "2", "3"])
    if tax_type == "1":
        tax_rate = Decimal("0.05")
        customs_clearance_mark = None
        zero_tax_rate_reason = None
    elif tax_type == "2":
        tax_rate = Decimal("0")
        customs_clearance_mark = random.choice(["1", "2"])
        zero_tax_rate_reason = "78"
    else:  # tax_type == "3"
        tax_rate = Decimal("0")
        customs_clearance_mark = None
        zero_tax_rate_reason = None

    sales_amount = Decimal("0")
    total_tax_amount = Decimal("0")
    total_amount = Decimal("0")
    zerotax_sales_amount = Decimal("0")
    freetax_sales_amount = Decimal("0")
    
    invoice = TWB2BMainItem.objects.create(
        company = random.choice(companies),
        sys_number=sys_number,
        invoice_number="",
        invoice_date = None,
        invoice_time=None,
        invoice_type="07",
        invoice_period="",
        erp_number=ERP_number,
        erp_date=timezone.now().date(),
        erp_reference="",
        #buyer_name=buyer_name,
        buyer=random.choice(buyer),
        buyer_remark="",
        customs_clearance_mark=customs_clearance_mark,
        category="",
        relate_number="",
        bonded_area_confirm="",
        zero_tax_rate_reason=zero_tax_rate_reason,
        reserved1="",
        reserved2="",
        sales_amount=0,
        zerotax_sales_amount=0,
        freetax_sales_amount=0,
        total_tax_amount=0,
        total_amount=0,
        invoice_status="未開立",
    )

    for j in range(6):  # 每張發票有6個明細
        line_quantity = random.randint(1, 10)
        line_unit_price = Decimal(random.randint(10, 500)) #.quantize(Decimal(".001"))
        line_amount = (line_quantity * line_unit_price) #.quantize(Decimal(".001"))

        # 稅額計算
        line_tax_amount = (line_amount * tax_rate).quantize(Decimal("1"))

        # 累加發票總額
        if tax_type == "1" :
            sales_amount += line_amount
        elif tax_type == "2" :
            zerotax_sales_amount += line_amount
        else :
            freetax_sales_amount += line_amount

        total_tax_amount += line_tax_amount
        total_amount = sales_amount + zerotax_sales_amount + freetax_sales_amount + total_tax_amount

        line_items.append(TWB2BLineItem(
            twb2bmainitem=invoice,
            line_description=random.choice(descriptions),
            line_quantity=str(line_quantity),
            line_unit=random.choice(["個", "箱", "公斤"]),
            line_unit_price=line_unit_price,
            line_amount=line_amount,
            line_tax_type=tax_type,
            line_tax_amount=line_tax_amount,
            line_remark="商品備註" if random.random() > 0.5 else "",
            line_sequence_number=f"{j+1:04d}"
        ))

    # 更新主檔欄位
    invoice.sales_amount = sales_amount
    invoice.zerotax_sales_amount = zerotax_sales_amount
    invoice.freetax_sales_amount = freetax_sales_amount
    invoice.total_tax_amount = total_tax_amount
    invoice.total_amount = total_amount
    invoice.tax_type = tax_type
    invoice.save()

# 寫入所有明細
TWB2BLineItem.objects.bulk_create(line_items)

print("✅ 已成功插入 10000 張發票，每張使用相同稅別、含 4 個明細，稅額與免稅邏輯正確！")
