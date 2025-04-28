    
class TWB2BMainItem(models.Model):
    company_id = models.ForeignKey('Company',
        on_delete=models.PROTECT,
        to_field='company_id',
        db_column='company_id',
        )
    B2B_B2C_CHOICES = [
        ('B2B', 'B2B'),
        ('B2C', 'B2C')
    ]
    b2b_b2c = models.CharField(max_length=3, choices=B2B_B2C_CHOICES)   # 電子發票類型B2B 或 B2C
    sys_number = models.CharField(max_length=20)    # 平台文件號碼
    sys_date = models.DateTimeField(blank=True, null=True)    #  平台傳送日期
    invoice_number = models.CharField(max_length=10, blank=True, null=True)     #  發票號碼  
    invoice_date = models.DateField(blank=True, null=True)    # 發票日期 (產出轉換8碼)
    invoice_time = models.TimeField(blank=True, null=True)   # 發票時間
    invoice_period = models.CharField(max_length=5, blank=True, null=True)    # 發票期別
    invoice_type = models.CharField(max_length=2, default='07', blank=True, null=True)     # 發票類別，預設07
 
    erp_number = models.CharField(max_length=20)    # ERP文件號碼
    erp_date = models.DateTimeField()   # ERP過帳日期
    erp_reference = models.CharField(max_length=60, blank=True, null=True)   # ERP備註資訊
  
    seller_bp_id = models.CharField(max_length=20, blank=True, null=True)     # 賣方客戶編號
    buyer_Identifier = models.CharField(max_length=10)   # 買方統一編號
    buyer_name = models.CharField(max_length=60, blank=True, null=True)   # 買方名稱
    buyer_bp_id = models.CharField(max_length=20, blank=True, null=True)    # 買方客戶編號
    buyer_remark = models.CharField(max_length=40, blank=True, null=True)    # 買方註記欄
    main_remark = models.CharField(max_length=200, blank=True, null=True)    # 總備註
 
    customs_clearance_mark = models.CharField(max_length=1, blank=True, null=True)     # 通關方式註記
    category = models.CharField(max_length=2, blank=True, null=True)   # 沖帳別
    relate_number = models.CharField(max_length=20, blank=True, null=True)   # 相關號碼
    bonded_area_confirm = models.CharField(max_length=1, blank=True, null=True)    # 買受人簽署適用零稅率註記
    zero_tax_rate_reason = models.CharField(max_length=2, blank=True, null=True)   # 零稅率原因
    reserved1 = models.CharField(max_length=20, blank=True, null=True)   # 保留欄位1
    reserved2 = models.CharField(max_length=100, blank=True, null=True)   # 保留欄位2
 
    sales_amount = models.DecimalField(max_digits=13, decimal_places=7, blank=True, null=True)    # 應稅銷售額合計(未稅)
    freetax_sales_amount = models.DecimalField(max_digits=13, decimal_places=7, blank=True, null=True)    # 免稅銷售額合計(未稅)
    zerotax_sales_amount = models.DecimalField(max_digits=13, decimal_places=7, blank=True, null=True)    # 零稅銷售額合計(未稅)
    TAX_TYPE_CHOICES = [
        ('1', '應稅'),
        ('2', '零稅率'),
        ('3', '免稅')       
    ]
    tax_type = models.CharField(max_length=1, choices=TAX_TYPE_CHOICES)   # 課稅別(1：應稅；2：零稅率；3：免稅)
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2)     # 稅率
    total_tax_amount = models.DecimalField(max_digits=20, decimal_places=0)     # 營業稅額總計
    total_amount = models.DecimalField(max_digits=13, decimal_places=7)   # 銷售額總計(含稅)
 
    original_currency_amount = models.DecimalField(max_digits=13, decimal_places=7, blank=True, null=True)    # 原幣金額
    exchange_rate = models.DecimalField(max_digits=8, decimal_places=5, blank=True, null=True)    # 匯率
    currency = models.CharField(max_length=3, blank=True, null=True)     # 幣別
    INVOICE_STATUS_CHOICES = [
        ('未開立', '未開立'),
        ('已開立', '已開立'),
        ('已作廢', '已作廢')
    ]
    invoice_status = models.CharField(max_length=6, choices=INVOICE_STATUS_CHOICES, default='未開立')     # 發票開立狀態：未開立/已開立/已作廢
    mof_date = models.DateField(blank=True, null=True)     #    稅局回應日
    mof_respone = models.CharField(max_length=200, blank=True, null=True)     # 稅局回應
    mof_reason = models.CharField(max_length=200, blank=True, null=True)     # 稅局拒絕理由
    creator = models.CharField(max_length=10, blank=True, null=True)       # 建立者
    creator_remark = models.CharField(max_length=200, blank=True, null=True)     # 平台備註
  
    def __str__(self):
        return f"{self.sys_number} - {self.erp_number} - {self.buyer_Identifier}"


class TWB2BLineItem(models.Model):
    main_item = models.ForeignKey('TWB2BMainItem', on_delete=models.CASCADE, related_name='line_items') 對應主表

    erp_number = models.CharField(max_length=20)    # ERP文件號碼(主表也有，自己用便於快速查找)
    line_sequence_number = models.CharField(max_length=4)     # 明細排列序號
    line_description = models.CharField(max_length=500)     # 品名
    line_quantity = models.DecimalField(max_digits=13, decimal_places=7)     # 數量
    line_unit = models.CharField(max_length=6, blank=True, null=True)     # 單位
    line_unit_price = models.DecimalField(max_digits=13, decimal_places=7)     # 單價
    LINE_TAX_TYPE_CHOICES = [
        ('1', '應稅'),
        ('2', '零稅率'),
        ('3', '免稅')       
    ]    
    line_tax_type = models.CharField(max_length=1, choices=LINE_TAX_TYPE_CHOICES)     # 課稅別 (1：應稅；2：零稅率；3：免稅)
    line_amount = models.DecimalField(max_digits=13, decimal_places=7)     # 金額 (B2B為未稅)
    line_remark = models.CharField(max_length=120, blank=True, null=True)     # 單一欄位備註
    line_relate_number = models.CharField(max_length=50, blank=True, null=True)     # line相關號碼
 
  
    def __str__(self):
        return f"{self.main_item.invoice_number or 'N/A'} - {self.erp_number} - {self.line_sequence_number} - {self.line_description[:30]}"

        
class TWAllowance(models.Model):
    company = models.ForeignKey('Company',
        on_delete=models.PROTECT,
        to_field='company_id',
        db_column='company_id',
        )

    # 發票來源
    b2b_b2c = models.CharField(max_length=3, choices=[('B2B','B2B'), ('B2C','B2C')])   # 折讓單發票類型B2B 或 B2C
    sys_number = models.CharField(max_length=20)    # 平台文件號碼
    sys_date = models.DateTimeField(blank=True, null=True)    #  平台日期
    allowance_number = models.CharField(max_length=16, blank=True, null=True)     #  折讓證明單號碼  
    allowance_date = models.DateField(blank=True, null=True)    # 折讓證明單日期 (產出轉換8碼)
    allowance_period = models.CharField(max_length=5, blank=True, null=True)    # 折讓期別
    allowance_type = models.CharField(max_length=2, default='02', blank=True, null=True)     # 折讓類別，預設為2

    erp_number = models.CharField(max_length=20)    # ERP文件號碼
    erp_date = models.DateTimeField()   # ERP過帳日期
    erp_reference = models.CharField(max_length=60, blank=True, null=True)   # ERP備註資訊
  
    seller_bp_id = models.CharField(max_length=20, blank=True, null=True)     # 賣方客戶編號
    buyer_Identifier = models.CharField(max_length=10)   # 買方統一編號
    buyer_name = models.CharField(max_length=60, blank=True, null=True)   # 買方名稱
    buyer_bp_id = models.CharField(max_length=20, blank=True, null=True)    # 買方客戶編號

    line_sequence_number = models.CharField(max_length=4)     # 明細排列序號
    line_original_invoice_date = models.DateField(blank=True, null=True)    # 發票日期 (產出轉換8碼)
    line_original_invoice_number = models.CharField(max_length=10, blank=True, null=True)     #  發票號碼  
    line_description = models.CharField(max_length=500)     # 品名
    line_quantity = models.DecimalField(max_digits=13, decimal_places=7)     # 數量
    line_unit = models.CharField(max_length=6, blank=True, null=True)     # 單位
    line_unit_price = models.DecimalField(max_digits=13, decimal_places=7)     # 單價
    LINE_TAX_TYPE_CHOICES = [
        ('1', '應稅'),
        ('2', '零稅率'),
        ('3', '免稅')       
    ]    
    line_tax_type = models.CharField(max_length=1, choices=LINE_TAX_TYPE_CHOICES)     # 課稅別 (1：應稅；2：零稅率；3：免稅)
    line_allowance_amount = models.DecimalField(max_digits=13, decimal_places=7)     # 金額 (未稅)
    line_allowance_tax = models.DecimalField(max_digits=20, decimal_places=0)     # 營業稅額

    allowance_amount = models.DecimalField(max_digits=13, decimal_places=7)     # 未稅總計
    allowance_tax = models.DecimalField(max_digits=20, decimal_places=0)     # 營業稅額總計

    ALLOWANCE_STATUS_CHOICES = [
        ('未開立', '未開立'),
        ('已開立', '已開立'),
        ('已作廢', '已作廢')
    ]
    allowance_status = models.CharField(max_length=6, choices=ALLOWANCE_STATUS_CHOICES, default='未開立')     # 折讓單開立狀態：未開立/已開立/已作廢
    mof_date = models.DateField(blank=True, null=True)     #    稅局回應日
    mof_respone = models.CharField(max_length=200, blank=True, null=True)     # 稅局回應
    mof_reason = models.CharField(max_length=200, blank=True, null=True)     # 稅局拒絕理由
    creator = models.CharField(max_length=10, blank=True, null=True)       # 建立者
    creator_remark = models.CharField(max_length=200, blank=True, null=True)     # 平台備註
  
    def __str__(self):
        return f"{self.allowance_number or '未編號'} - {self.erp_number} - {self.buyer_Identifier} - {self.buyer_name}"



