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
    item_quantity = models.IntegerField(max_length=50)
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
    corporate_id =  models.CharField(max_length=8)
    invoice_number = models.CharField(max_length=20, unique=True)  # 發票號碼
    invoice_date = models.DateField()  # 發票日期
    invoice_time = models.TimeField()  # 發票時間
    seller_name = models.CharField(max_length=225)  # 賣方
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
    quantity = models.DecimalField(max_digits=20, decimal_places=7)  # 數量
    unit = models.CharField(max_length=6, blank=True, null=True)  # 單位
    unit_price = models.DecimalField(max_digits=20, decimal_places=7)  # 單價
    tax_type = models.CharField(max_length=50)  # 課稅別
    amount = models.DecimalField(max_digits=20, decimal_places=7)  # 金額
    sequence_number = models.CharField(max_length=4)  # 明細排列序號
    remark = models.CharField(max_length=120, blank=True, null=True)  # 單一欄位備註
    relate_number = models.CharField(max_length=50, blank=True, null=True)  # 相關號碼
    #invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name="amount_details")
    sales_amount = models.DecimalField(max_digits=20, decimal_places=0)  # 銷售額合計
    tax_type = models.CharField(max_length=50)  # 課稅別
    tax_rate = models.CharField(max_length=50)  # 稅率
    tax_amount = models.DecimalField(max_digits=20, decimal_places=0)  # 營業稅額
    total_amount = models.DecimalField(max_digits=20, decimal_places=0)  # 總計
    discount_amount = models.DecimalField(max_digits=20, decimal_places=0, blank=True, null=True)  # 扣抵金額
    original_currency_amount = models.DecimalField(max_digits=20, decimal_places=7, blank=True, null=True)  # 原幣金額
    exchange_rate = models.DecimalField(max_digits=13, decimal_places=5, blank=True, null=True)  # 匯率
    currency = models.CharField(max_length=10, blank=True, null=True)  # 幣別

	
	
# Create your models here.
