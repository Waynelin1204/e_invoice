from django  import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from django.db import models



class TWB2BMainItem(models.Model):
    company = models.ForeignKey("e_invoices.Company", on_delete=models.CASCADE, related_name="twb2bmainitem_invoices")  # 公司代碼
    company_code = models.CharField(max_length=10, blank=True, null=True)  # 公司代碼
    B2B_B2C_CHOICES = [
        ('B2B', 'B2B'),
        ('B2C', 'B2C')
    ]
    b2b_b2c = models.CharField(max_length=3, choices=B2B_B2C_CHOICES) # 電子發票類型B2B 或 B2C
    sys_number = models.CharField(max_length=20) # 平台文件號碼
    sys_date = models.DateTimeField(blank=True, null=True)    #  平台傳送日期
    invoice_number = models.CharField(max_length=10, blank=True, null=True)     #  發票號碼  
    invoice_date = models.DateField(max_length=8,blank=True, null=True) # 平台傳送日期
    invoice_time = models.CharField(max_length=8, blank=True, null=True) # 發票時間
    invoice_period = models.CharField(max_length=5,blank=True, null=True)  # 期別
    invoice_type = models.CharField(max_length=2,blank=True, null=True)  # 發票類別

    erp_number = models.CharField(max_length=10)  # ERP文件號碼
    erp_date = models.DateField(max_length=8)
    erp_reference = models.CharField(max_length=60, blank=True, null=True) # ERP備註資訊
    
    company_identifier = models.CharField(max_length=60, blank=True, null=True) 
    seller_bp_id = models.CharField(max_length=20, blank=True, null=True)
    tax_identifier = models.CharField(max_length=10, blank=True, null=True) 
    seller_name = models.CharField(max_length=60,blank=True, null=True)
    buyer_identifier = models.CharField(max_length=10,blank=True, null=True)
    buyer_name = models.CharField(max_length=60,blank=True, null=True)
    buyer_bp_id = models.CharField(max_length=20, blank=True, null=True)
    buyer_remark = models.CharField(max_length=1, blank=True, null=True)
    main_remark = models.CharField(max_length=200, blank=True, null=True)
    group_mark = models.CharField(max_length=1, blank=True, null=True)  # 彙開註記
    donate_mark = models.CharField(max_length=10)  # 捐贈註記


    customs_clearance_mark = models.CharField(max_length=1, blank=True, null=True)
    category = models.CharField(max_length=2, blank=True, null=True)
    relate_number = models.CharField(max_length=20, blank=True, null=True)
    invoice_type = models.CharField(max_length=2,blank=True, null=True)
    bonded_area_confirm = models.CharField(max_length=1, blank=True, null=True)
    zero_tax_rate_reason = models.CharField(max_length=2, blank=True, null=True)
    reserved1 = models.CharField(max_length=20, blank=True, null=True)
    reserved2 = models.CharField(max_length=100, blank=True, null=True)

    sales_amount = models.DecimalField(max_digits=13, decimal_places=7)
    freetax_sales_amount = models.DecimalField(max_digits=13, decimal_places=7,blank=True, null=True)
    zerotax_sales_amount = models.DecimalField(max_digits=13, decimal_places=7,blank=True, null=True)
    tax_type = models.CharField(
        choices=[('1', '應稅'), ('2', '零稅率'), ('3', '免稅')], max_length=1, blank=True, null=True) #課稅別(1：應稅；2：零稅率；3：免稅)
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2,blank=True, null=True)
    total_tax_amount = models.DecimalField(max_digits=20, decimal_places=0,blank=True, null=True)
    
    total_amount = models.DecimalField(max_digits=13, decimal_places=7,blank=True, null=True)
    original_currency_amount = models.DecimalField(max_digits=13, decimal_places=7, blank=True, null=True)
    exchange_rate = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True)
    currency = models.CharField(max_length=3, blank=True, null=True)
    invoice_status = models.CharField(max_length=10, blank=True, null=True, default='未開立')

    description = models.CharField(max_length=255, blank=True, null=True)
    remark = models.CharField(max_length=120, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=13, decimal_places=7, blank=True, null=True)
    payment_status = models.CharField(max_length=10, blank=True, null=True)
    invoice_status = models.CharField(max_length=10, blank=True, null=True)
    void_status = models.CharField(max_length=10, blank=True, null=True)
    mof_date = models.DateField(blank=True, null=True)     #    稅局回應日
    mof_respone = models.CharField(max_length=200, blank=True, null=True)     # 稅局回應
    mof_reason = models.CharField(max_length=200, blank=True, null=True)     # 稅局拒絕理由
    creator = models.CharField(max_length=10, blank=True, null=True)       # 建立者
    creator_remark = models.CharField(max_length=200, blank=True, null=True)     # 平台備註
    
    cancel_date = models.DateField(blank=True, null=True)   # 作廢發票日期 (產出轉換8碼)
    cancel_time = models.TimeField(blank=True, null=True)   # 作廢發票時間
    cancel_period = models.CharField(max_length=5, blank=True, null=True)    # 作廢發票期別
    cancel_reason = models.CharField(max_length=20, blank=True, null=True)     # 作廢原因
    returntax_document_number = models.CharField(max_length=60, blank=True, null=True)     # 專案作廢核准文號
    cancel_remark = models.CharField(max_length=200, blank=True, null=True)     # 作廢備註
    cancel_mof_date = models.DateField(blank=True, null=True)     #    稅局回應日
    cancel_mof_respone = models.CharField(max_length=200, blank=True, null=True)     # 稅局回應
    cancel_mof_reason = models.CharField(max_length=200, blank=True, null=True)     # 稅局拒絕理由

   # 稅局拒絕理由
    def __str__(self):
        return f"{self.sys_number} - {self.company_code}"

class TWB2BLineItem(models.Model):
    twb2bmainitem = models.ForeignKey(TWB2BMainItem, related_name='items', on_delete=models.CASCADE)  # TWB2BMainItem
    line_description = models.CharField(max_length=500,blank=True, null=True)  # 品名
    line_tax_type = models.CharField(choices=[(1, '應稅'), (2, '零稅率'), (3, '免稅')], max_length=1, blank=True, null=True)
    line_quantity = models.CharField(max_length=50,blank=True, null=True)  # 數量 (可支援 '3C商品' 這類非數值)
    line_unit = models.CharField(max_length=6, blank=True, null=True)  # 單位
    line_unit_price = models.DecimalField(max_digits=20, decimal_places=7,blank=True, null=True)  # 單價
    line_amount = models.DecimalField(max_digits=20, decimal_places=7,blank=True, null=True)  # 金額
    line_remark = models.CharField(max_length=200, blank=True, null=True)  # 備註
    line_sequence_number = models.CharField(max_length=4,blank=True, null=True)  # 明細排列序號
    line_relate_number = models.CharField(max_length=4,blank=True, null=True)  # 明細排列序號
    line_tax_amount = models.DecimalField(max_digits=20, decimal_places=7,blank=True, null=True)
    line_sales_amount = models.DecimalField(max_digits=20, decimal_places=7,blank=True, null=True)
    line_tax_type = models.CharField(max_length=1,blank=True, null=True)