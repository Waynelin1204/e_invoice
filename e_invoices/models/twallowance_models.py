from django  import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum
from django.db import models

class TWAllowance(models.Model):
    company = models.ForeignKey("e_invoices.Company", on_delete=models.CASCADE, related_name="twallowance")  # 公司代碼
    # 發票來源
    b2b_b2c = models.CharField(max_length=3, choices=[('B2B','B2B'), ('B2C','B2C')])   # 折讓單發票類型B2B 或 B2C
    sys_number = models.CharField(max_length=20)    # 平台文件號碼
    sys_date = models.DateTimeField(blank=True, null=True)    #  平台日期
    export_date = models.DateTimeField(blank=True, null=True)    #  平台匯出日期
    allowance_number = models.CharField(max_length=16, blank=True, null=True)     #  折讓證明單號碼  
    allowance_date = models.DateField(blank=True, null=True)    # 折讓證明單日期 (產出轉換8碼)
    allowance_time = models.DateTimeField(blank=True, null=True)    # 折讓證明單日期 (產出轉換8碼)
    allowance_period = models.CharField(max_length=5, blank=True, null=True)    # 折讓期別
    allowance_type = models.CharField(max_length=2, default='02', blank=True, null=True)     # 折讓類別，預設為2

    erp_number = models.CharField(max_length=20)    # ERP文件號碼
    erp_date = models.DateTimeField()   # ERP過帳日期
    erp_reference = models.CharField(max_length=60, blank=True, null=True)   # ERP備註資訊

    seller_bp_id = models.CharField(max_length=20, blank=True, null=True)     # 賣方客戶編號
    buyer_identifier = models.CharField(max_length=10)   # 買方統一編號
    buyer_name = models.CharField(max_length=60, blank=True, null=True)   # 買方名稱
    buyer_bp_id = models.CharField(max_length=20, blank=True, null=True)    # 買方客戶編號

    allowance_amount = models.DecimalField(max_digits=13, decimal_places=7, blank=True, null=True)     # 未稅總計
    allowance_tax = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True)     # 營業稅額總計
    allowance_status = models.CharField(max_length=6, default='未開立',blank=True, null=True)     # 折讓單開立狀態：未開立/已開立/已作廢
    mof_date = models.DateField(blank=True, null=True)     #    稅局回應日
    mof_respone = models.CharField(max_length=200, blank=True, null=True)     # 稅局回應
    mof_reason = models.CharField(max_length=200, blank=True, null=True)     # 稅局拒絕理由
    creator = models.CharField(max_length=10, blank=True, null=True)       # 建立者
    creator_remark = models.CharField(max_length=200, blank=True, null=True)     # 平台備註
    allowance_cancel_date = models.DateField(blank=True, null=True)   # 作廢折讓單日期 (產出轉換8碼)
    allowance_cancel_time = models.TimeField(blank=True, null=True)   # 作廢折讓單時間
    allowance_cancel_reason = models.CharField(max_length=20, blank=True, null=True)     # 作廢折讓單原因
    allowance_cancel_remark = models.CharField(max_length=200, blank=True, null=True)     # 作廢折讓單備註
    cancel_mof_date = models.DateField(blank=True, null=True)     # 稅局回應日
    cancel_mof_respone = models.CharField(max_length=200, blank=True, null=True)     # 稅局回應
    cancel_mof_reason = models.CharField(max_length=200, blank=True, null=True)     # 稅局拒絕理由
   
    def __str__(self):
        return f"{self.allowance_number}"
    
class TWAllowanceLineItem(models.Model):
    twallowance = models.ForeignKey(TWAllowance, related_name='items', on_delete=models.CASCADE)  # TWB2BMainItem
    line_sequence_number = models.CharField(max_length=4, blank=True, null=True)     # 明細排列序號
    line_original_invoice_date = models.DateField(blank=True, null=True)    # 發票日期 (產出轉換8碼)
    line_original_invoice_number = models.CharField(max_length=10, blank=True, null=True)     #  發票號碼 
    linked_invoice = models.ForeignKey('TWB2BMainItem',null=True,blank=True,on_delete=models.SET_NULL, related_name='allowance_lineitems')  # 建議加上這一行
    line_description = models.CharField(max_length=500,blank=True, null=True)     # 品名
    line_quantity = models.CharField(max_length=10 ,blank=True, null=True)     # 數量
    line_unit = models.CharField(max_length=4, blank=True, null=True)     # 單位
    line_unit_price = models.DecimalField(max_digits=13, decimal_places=3, blank=True, null=True)     # 單價
    LINE_TAX_TYPE_CHOICES = [
        ('1', '應稅'),
        ('2', '零稅率'),
        ('3', '免稅')       
    ]    
    line_tax_type = models.CharField(max_length=1, choices=LINE_TAX_TYPE_CHOICES,blank=True, null=True)     # 課稅別 (1：應稅；2：零稅率；3：免稅)
    line_allowance_amount = models.DecimalField(max_digits=13, decimal_places=3,blank=True, null=True)     # 金額 (未稅)
    line_allowance_tax = models.DecimalField(max_digits=20, decimal_places=3,blank=True, null=True)     # 營業稅額
    INVOICE_CANCEL_STATUS_CHOICES = [
        ('0', '未作廢'),
        ('1', '已作廢')       
    ]    
    line_invoice_cancel_status = models.CharField(max_length=20, choices=INVOICE_CANCEL_STATUS_CHOICES, null=True, blank=True)
