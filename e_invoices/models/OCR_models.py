from django  import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from django.db import models

class Ocr(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True)  # 發票號碼
    random_code = models.CharField(max_length=4, blank=True, null=True)  # 隨機碼
    invoice_date = models.DateField()  # 發票日期
    buyer_tax_id = models.CharField(max_length=8, blank=True, null=True)  # 買方統一編號
    seller_tax_id = models.CharField(max_length=8)  # 賣方統一編號
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # 總金額
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # 稅額

class Ocritem(models.Model):
    ocr = models.ForeignKey(Ocr, related_name='items', on_delete=models.CASCADE)  # 關聯發票
    product_name = models.CharField(max_length=255)  # 品名
    quantity = models.CharField(max_length=50)  # 數量 (String to handle non-numeric values like '3C商品')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # 單價	

class Twa0101(models.Model):
    data_type = models.CharField(max_length=4) # Consistent H1 
    job_type = models.CharField(max_length=4) # H or G
    corporate_id =  models.CharField(max_length=8) #統一編號
    invoice_number = models.CharField(max_length=20, blank=True, null=True)  # 後來才有
    invoice_date = models.DateField()  # 發票日期
    invoice_time = models.TimeField()  # 發票時間
    seller_name = models.CharField(max_length=225)  # 賣方
    company = models.ForeignKey("e_invoices.Company", on_delete=models.CASCADE, related_name="twa0101_invoices")  # 公司代碼
    buyer_name = models.CharField(max_length=225)  # 買方
    buyer_remark = models.CharField(max_length=200, blank=True, null=True)  # 買方註記欄
    main_remark = models.CharField(max_length=200, blank=True, null=True)  # 總備註
    customs_clearance_mark = models.CharField(max_length=10, blank=True, null=True)  # 通關方式註記
    category = models.CharField(max_length=2, blank=True, null=True)  # 沖帳別
    relate_number = models.CharField(max_length=20, blank=True, null=True)  # 相關號碼
    invoice_type = models.CharField(max_length=50)  # 發票類別
    group_mark = models.CharField(max_length=1, blank=True, null=True)  # 彙開註記
    donate_mark = models.CharField(max_length=10)  # 捐贈註記
    zero_tax_rate_reason = models.CharField(max_length=50, blank=True, null=True)  # 零稅率原因
    reserved1 = models.CharField(max_length=20, blank=True, null=True)  # 保留欄位1
    reserved2 = models.CharField(max_length=100, blank=True, null=True)  # 保留欄位2
    #invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")
    description = models.CharField(max_length=500)  # 品名
    quantity = models.DecimalField(max_digits=20, decimal_places=7, blank=True, null=True) # 數量
    unit = models.CharField(max_length=6, blank=True, null=True)  # 單位
    unit_price = models.DecimalField(max_digits=20, decimal_places=7,blank=True, null=True)  # 單價
    tax_type = models.CharField(max_length=50, blank=True, null=True)  # 課稅別
    amount = models.DecimalField(max_digits=20, decimal_places=7, blank=True, null=True)  # 金額
    sequence_number = models.CharField(max_length=4,blank=True, null=True)  # 明細排列序號
    remark = models.CharField(max_length=120, blank=True, null=True)  # 單一欄位備註
    relate_number = models.CharField(max_length=50, blank=True, null=True)  # 相關號碼
    #invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name="amount_details")
    sales_amount = models.DecimalField(max_digits=20, decimal_places=0,blank=True, null=True)  # 銷售額合計
    tax_type = models.CharField(max_length=50,blank=True, null=True)  # 課稅別
    tax_rate = models.CharField(max_length=50,blank=True, null=True)  # 稅率
    tax_amount = models.DecimalField(max_digits=20, decimal_places=0)  # 營業稅額
    total_amount = models.DecimalField(max_digits=20, decimal_places=0,blank=True, null=True)  # 總計
    discount_amount = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True)  # 扣抵金額
    original_currency_amount = models.DecimalField(max_digits=20, decimal_places=7, blank=True, null=True)  # 原幣金額
    exchange_rate = models.DecimalField(max_digits=13, decimal_places=5, blank=True, null=True)  # 匯率
    currency = models.CharField(max_length=10, blank=True, null=True)  # 幣別
    payment_status = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    uniform_invoice_number = models.CharField(max_length=10, blank=True, null=True)
    invoice_status = models.CharField(max_length=10, blank=True, null=True, default='未開立')
    void_status = models.CharField(max_length=10, blank=True, null=True)
    
    def __str__(self):
        return f"{self.relate_number} - {self.buyer_name}"
    
class Twa0101Item(models.Model):
    twa0101 = models.ForeignKey(Twa0101, related_name='items', on_delete=models.CASCADE)  # 關聯 Twa0101
    product_name = models.CharField(max_length=500)  # 品名
    quantity = models.CharField(max_length=50)  # 數量 (可支援 '3C商品' 這類非數值)
    unit = models.CharField(max_length=6, blank=True, null=True)  # 單位
    unit_price = models.DecimalField(max_digits=20, decimal_places=7)  # 單價
    amount = models.DecimalField(max_digits=20, decimal_places=7)  # 金額
    remark = models.CharField(max_length=200, blank=True, null=True)  # 備註
    sequence_number = models.CharField(max_length=4)  # 明細排列序號

    def __str__(self):
        return f"{self.product_name} ({self.quantity}) - {self.amount}"