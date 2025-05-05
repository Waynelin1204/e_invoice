from django  import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from django.db import models

# 僅限英數字
alphanumeric_validator = RegexValidator(r'^[a-zA-Z0-9]{1,10}$')
# 僅限數字
digit_validator = RegexValidator(r'^[0-9]+$')
class Company(models.Model):
    # 營業人代碼
    company_id = models.CharField(
        max_length=10,
        validators=[alphanumeric_validator],
        error_messages={'invalid': '請輸入10碼以內字元，僅限英文大小寫或數字'},
        primary_key=True
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
    tax_identifier = models.CharField(
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
        return f"{self.company_id}"