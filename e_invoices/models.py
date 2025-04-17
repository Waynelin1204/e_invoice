from django  import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from django.db import models



        
            
class Invoice(models.Model):

    STATUS_CHOICES = [
        ('created', 'eDocument created'),
        ('error', 'Error'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    # Document reference

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    document_id = models.CharField(max_length=50, unique=True)
    invoicetypecode = models.CharField(max_length=20)
    issue_date = models.CharField(max_length=20)
    issue_time = models.CharField(max_length=20)
    document_currency = models.CharField(max_length=10)
    self_billing = models.CharField(max_length=5)
    buyer_reference = models.CharField(max_length=50)

    # Supplier details
    supplier_name = models.CharField(max_length=100)
    supplier_tin_id = models.CharField(max_length=50)
    supplier_brn_id = models.CharField(max_length=50)
    supplier_id = models.CharField(max_length=50)
    supplier_addr1 = models.CharField(max_length=100)
    supplier_addr2 = models.CharField(max_length=100, blank=True, null=True)
    supplier_addr3 = models.CharField(max_length=100, blank=True, null=True)
    supplier_addr4 = models.CharField(max_length=100, blank=True, null=True)
    supplier_country = models.CharField(max_length=50)
    supplier_scheme_id = models.CharField(max_length=50)
    supplier_legal_name = models.CharField(max_length=100)
    supplier_phone = models.CharField(max_length=20)

    # Buyer details
    buyer_name = models.CharField(max_length=100)
    buyer_supp_assign_id = models.CharField(max_length=50)
    buyer_id = models.CharField(max_length=50)
    buyer_tin_id = models.CharField(max_length=50)
    buyer_brn_id = models.CharField(max_length=50)
    buyer_addr1 = models.CharField(max_length=100)
    buyer_addr2 = models.CharField(max_length=100, blank=True, null=True)
    buyer_addr3 = models.CharField(max_length=100, blank=True, null=True)
    buyer_addr4 = models.CharField(max_length=100, blank=True, null=True)
    buyer_scheme_id = models.CharField(max_length=50)
    buyer_legal_name = models.CharField(max_length=100)
    buyer_phone = models.CharField(max_length=20)
    buyer_email = models.EmailField(max_length=100)
    buyer_country = models.CharField(max_length=50)
    buyer_account_name = models.CharField(max_length=100)
    buyer_account_phone = models.CharField(max_length=20)
    buyer_account_email = models.EmailField(max_length=100)

    # Delivery details
    delivery_addr1 = models.CharField(max_length=100)
    delivery_addr2 = models.CharField(max_length=100, blank=True, null=True)
    delivery_addr3 = models.CharField(max_length=100, blank=True, null=True)
    delivery_addr4 = models.CharField(max_length=100, blank=True, null=True)
    delivery_country = models.CharField(max_length=50)
    delivery_tin_id = models.CharField(max_length=50)
    delivery_name = models.CharField(max_length=100)
    delivery_id = models.CharField(max_length=50)
    delivery_scheme_id = models.CharField(max_length=50)

    # Tax details
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2)
    taxable_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_category = models.CharField(max_length=50)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2)
    tax_scheme_id = models.CharField(max_length=50)
    tax_scheme_name = models.CharField(max_length=100)
    tax_exemption = models.CharField(max_length=100)

    # Amounts
    line_ext_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_exclus_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_includ_amount = models.DecimalField(max_digits=12, decimal_places=2)
    prepaid_amount = models.CharField(max_length=100, blank=True, null=True)
    payable_amount = models.CharField(max_length=100, blank=True, null=True)

    # Item details
    item_id = models.CharField(max_length=50)
    item_quantity = models.IntegerField()
    item_name = models.CharField(max_length=100)
    item_unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    # File path
    xml_file_path = models.CharField(max_length=255)
    
    # Response
    response_code = models.CharField(max_length=255)
    clearance_reference_id = models.CharField(max_length=255)
    clearance_qrcode = models.CharField(max_length=255)
    clearance_status_code = models.CharField(max_length=255)
    clearance_reason = models.CharField(max_length=255)



    def __str__(self):
        return f"Invoice {self.document_id} - {self.status}"
    
    
# 僅限英數字
alphanumeric_validator = RegexValidator(r'^[a-zA-Z0-9]{1,10}$')
# 僅限數字
digit_validator = RegexValidator(r'^[0-9]+$')
class Company(models.Model):
    # 公司代碼
    company_id = models.CharField(
        max_length=10,
        validators=[alphanumeric_validator],
        error_messages={'invalid': '請輸入10碼以內字元，僅限英文大小寫或數字'}
    )

    # 統一編號
    company_identifier = models.CharField(
        max_length=8,
        validators=[RegexValidator(r'^\d{8}$', message='請輸入8碼數字')]
    )

    company_register_name = models.CharField(max_length=100) # 公司註冊名稱
    company_name = models.CharField(max_length=100) # 公司簡稱
    company_address = models.CharField(max_length=255) # 公司地址

    # 總公司
    head_company_identifer = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        limit_choices_to={'company_type': 0},  # 只選 Headquarter 當總公司
        related_name='branches'
    )

    # 公司類型
    company_type = models.IntegerField(
        choices=[(0, '總機構'), (1, '分支機構')],
        default=0  # 預設為'總機構'
    )

    # 是否為境外電商
    is_foreign_ecomm = models.IntegerField(
        choices=[(0, '否'), (1, '是')],
        default=0  # 預設為否
    )

    # 稅籍編號
    tax_identifer = models.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d{9}$', message='請輸入9碼數字')]
    )

    # 電子郵件地址
    email = models.CharField(
        max_length=100,
        validators=[RegexValidator(r'^.+@.+$', message='請輸入100碼以內含有「@」符號的電子郵件地址')],
        blank=True,
        null=True
    )

    # 申報期別
    reporting_period = models.IntegerField(
        choices=[(1, '單月'), (2, '雙月')],
        default=2  # 預設為雙月
    )
    
    def __str__(self):
        return f"{self.company_id} - {self.company_name}"
# class Company(models.Model):
    # name = models.CharField(max_length=255)
    # tax_id = models.CharField(max_length=8, unique=True)
    # parent_companies = models.ManyToManyField('self', symmetrical=False, related_name='subsidiary_companies', blank=True)

    # def __str__(self):
        # return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="users")  # 所屬公司
    #company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)  # or use `null=False` if mandatory
    viewable_companies = models.ManyToManyField(Company, related_name="viewable_by_users")  # 可查看的公司


    def __str__(self):
        return self.user.username
        
class RegisterForm(UserCreationForm):
    username = forms.CharField(
	label="Account",
	widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email= forms.EmailField(
	label="Email",
	widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    password1 = forms.CharField(
	label="Password",
	widget=forms.PasswordInput(attrs={'class': 'form-control'})
   )
    password2 = forms.CharField(
	label="Confirm Password",
	widget=forms.PasswordInput(attrs={'class': 'form-control'})
   )

class Meta:
    model = User
    field = ('username', 'email', 'password1', 'password2')

class LoginForm(forms.Form):

    username=forms.CharField(
        label="Account",
        widget=forms.TextInput(attrs={'class':'form-control'})
    )

    password=forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class':'form-control'})
    )

class Sapfagll03(models.Model):

    document_number = models.IntegerField()
    #document_number = models.CharField(max_length=20) 
    TAX_CODES = [
        ('U0','U0'),
        ('V0','V0'),
        ('A0','A0'),
        ('A1','A1')
    ]
    tax_code = models.CharField(max_length=4, choices=TAX_CODES) 
    DOCUMENT_TYPES = [
        ('DR', 'DR'),
        ('KR', 'KR'),
        ('KX', 'KX'),
        ('RV', 'RV'),
        ('RZ', 'RZ')
    ]
    document_type = models.CharField(max_length=5, choices=DOCUMENT_TYPES)
    posting_date = models.CharField(max_length=20) 
    document_currency = models.CharField(max_length=3)  
    amount_in_doc_curr = models.DecimalField(max_digits=15, decimal_places=2) 
    local_currency = models.CharField(max_length=3, blank=True, null=True)  
    amount_in_lc = models.DecimalField(max_digits=15, decimal_places=2)  
    reference = models.CharField(max_length=50, blank=True, null=True) 
    offsetting_account = models.CharField(max_length=20, blank=True, null=True)
    including_tax_amount = models.CharField(max_length=20, blank=True, null=True)



    def __str__(self):
        return f"Document {self.document_number} ({self.document_type})"
       


# class SAPFAGLL03(models.Model):
    # document_number = models.BigIntegerField(unique=True)  # ½T«O°ß¤@
    # tax_code = models.CharField(max_length=5)
    
    # DOCUMENT_TYPES = [
        # ('DR', 'Debit Record'),
        # ('KR', 'Credit Record'),
        # ('KX', 'Some Other Type'),
    # ]
    # document_type = models.CharField(max_length=5, choices=DOCUMENT_TYPES)
    
    # document_date = models.DateTimeField()
    # fiscal_year = models.PositiveIntegerField()
    # posting_date = models.DateTimeField()
    # posting_key = models.PositiveSmallIntegerField()
    
    # document_currency = models.CharField(max_length=3)
    # amount_in_doc_curr = models.DecimalField(max_digits=15, decimal_places=2)
    # local_currency = models.CharField(max_length=3)
    # amount_in_lc = models.DecimalField(max_digits=15, decimal_places=2)

    # text = models.TextField(blank=True)
    # assignment = models.CharField(max_length=20, blank=True)
    # cost_center = models.CharField(max_length=10, blank=True)
    # document_header_text = models.TextField(blank=True)
    # reference = models.CharField(max_length=20, blank=True)
    
    # year_month = models.CharField(
        # max_length=7, 
        # validators=[RegexValidator(regex=r'^\d{4}/\d{2}$', message="®æ¦¡À³¬° YYYY/MM")]
    # )
    
    # clearing_date = models.DateTimeField(null=True, blank=True)
    # clearing_document = models.CharField(max_length=50, blank=True)
    # vendor = models.CharField(max_length=50, blank=True)
    
    # profit_center = models.CharField(max_length=10, blank=True)
    # net_due_date = models.DateTimeField(null=True, blank=True)
    # reference_key_2 = models.CharField(max_length=50, blank=True)
    # reference_key_3 = models.CharField(max_length=50, blank=True)
    
    # order = models.CharField(max_length=50, blank=True)
    # offsetting_account = models.CharField(max_length=20, blank=True)
    # transaction_type = models.CharField(max_length=50, blank=True)
    # trading_partner_no = models.CharField(max_length=50, blank=True)

    # def __str__(self):
        # return f"Document {self.document_number} - {self.document_type}"
	


class Myinvoiceportal(models.Model):
	submissionUid = models.CharField(max_length=225, unique = True)
	longId = models.CharField(max_length=225)
	internalId = models.CharField(max_length=225)
	typeName = models.CharField(max_length=225)
	typeVersionName = models.CharField(max_length=225)
	issuerTin = models.CharField(max_length=225)
	issuerName = models.CharField(max_length=225)
	receiverId = models.CharField(max_length=225)
	receiverName = models.CharField(max_length=225)
	dateTimeIssued = models.CharField(max_length=225)
	dateTimeReceived =models.CharField(max_length=225)
	dateTimeValidated = models.CharField(max_length=225)
	totalPayableAmount = models.CharField(max_length=225)
	totalExcludingTax =models.CharField(max_length=225)
	totalDiscount = models.CharField(max_length=225)
	totalNetAmount = models.CharField(max_length=225)
	status = models.CharField(max_length=225)
	cancelDateTime = models.TextField(null=True, blank=True)
	rejectRequestDateTime = models.TextField(null=True, blank=True)
	documentStatusReason = models.TextField(null=True, blank=True)
	createdByUserId = models.CharField(max_length=225)
	
	@property
	def internal_id_trimmed(self):
		return self.internalId[:-4]
	
	
class Twa0101(models.Model):
    data_type = models.CharField(max_length=4) # Consistent H1 
    job_type = models.CharField(max_length=4) # H or G
    corporate_id =  models.CharField(max_length=8) #統一編號
    invoice_number = models.CharField(max_length=20, blank=True, null=True)  # 後來才有
    invoice_date = models.DateField()  # 發票日期
    invoice_time = models.TimeField()  # 發票時間
    seller_name = models.CharField(max_length=225)  # 賣方
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="twa0101_invoices")  # 公司代碼
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

class NumberDistribution(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='number_distributions')
    initial_char = models.CharField(max_length=2)  # 開頭字母
    period = models.CharField(max_length=5)  # 期別
    start_number = models.CharField(max_length=8) # 起始號碼
    end_number = models.CharField(max_length=8) # 結束號碼
    current_number = models.CharField(max_length=8, blank=True, null=True)  # 當前號碼
    last_used_date = models.DateField(blank=True, null=True)  # 最後使用日期
    status = models.CharField(max_length=10, choices=[('available', 'Available'), ('used', 'Used')], default='available')

    def __str__(self):
        return f"{self.company}"
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
	
# Create your models here.

class TWB2BMainItem(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="twb2bmainitem_invoices")  # 公司代碼
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
        choices=[(1, '應稅'), (2, '零稅率'), (3, '免稅')], max_length=1, blank=True, null=True) #課稅別(1：應稅；2：零稅率；3：免稅)
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
     
class TWAllowance(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="twallowance")  # 公司代碼
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

    allowance_status = models.CharField(max_length=6, default='未開立')     # 折讓單開立狀態：未開立/已開立/已作廢
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
