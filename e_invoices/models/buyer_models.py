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
class Buyer(models.Model):


    # 統一編號
    buyer_identifier = models.CharField(
        max_length=8,
        validators=[RegexValidator(r'^\d{8}$', message='請輸入8碼數字')],
        primary_key=True
    )

    # 營業人代碼
    buyer_bp_id = models.CharField(
        max_length=10,
        validators=[alphanumeric_validator],
        error_messages={'invalid': '請輸入10碼以內字元，僅限英文大小寫或數字'},
        blank = True,
        null = True
    )


    buyer_register_name = models.CharField(max_length=100 ,blank = True, null = True) # 公司註冊名稱
    buyer_name = models.CharField(max_length=100, blank = True, null = True) # 公司簡稱
    buyer_address = models.CharField(max_length=255 ,blank = True, null = True) # 公司地址

    # 稅籍編號
    buyer_tax_identifier = models.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d{9}$', message='請輸入9碼數字')],
        blank = True, 
        null = True
    )

    # 電子郵件地址
    buyer_email = models.CharField(
        max_length=100,
        validators=[RegexValidator(r'^.+@.+$', message='請輸入100碼以內含有「@」符號的電子郵件地址')],
        blank=True,
        null=True
    )
    
    exchange_mode = models.BooleanField(default=False,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "買家資料設定"
        verbose_name_plural = "買家資料設定"


    def __str__(self):
        return f"{self.buyer_bp_id}"