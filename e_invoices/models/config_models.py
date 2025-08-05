from django  import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from e_invoices.models import Company



class CompanyNotificationConfig(models.Model):
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="notification_config",
        verbose_name="所屬公司"
    )

    email_validator = RegexValidator(
        regex=r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$',
        message='請輸入有效的電子郵件格式'
    )

    output_email_address = models.CharField(
        max_length=100,
        validators=[email_validator],
        blank=True,
        null=True,
        verbose_name="通知收件者 Email"
    )

    # 發票通知開關
    issued_invoice_notification = models.BooleanField(default=True)
    canceled_invoice_notification = models.BooleanField(default=True)
    deleted_invoice_notification = models.BooleanField(default=True)

    # 折讓通知開關
    issued_allowance_notification = models.BooleanField(default=True)
    canceled_allowance_notification = models.BooleanField(default=True)
    deleted_allowance_notification = models.BooleanField(default=True)

    # =======================================================================================================
    
    # 資料夾路徑
    # 存證模式
    # 開立發票xml存放路徑
    output_dir_F0401 = models.CharField(max_length=255, blank=True, null=True, verbose_name="F0401 輸出路徑")

    # 存證模式
    # 作廢發票xml存放路徑
    output_dir_F0501 = models.CharField(max_length=255, blank=True, null=True, verbose_name="F0501 輸出路徑")

    # 存證模式   
    # 開立折讓單xml存放路徑
    output_dir_G0401 = models.CharField(max_length=255, blank=True, null=True, verbose_name="G0401 輸出路徑")

    # 存證模式    
    # 作廢折讓單xml存放路徑
    output_dir_G0501 = models.CharField(max_length=255, blank=True, null=True, verbose_name="G0501 輸出路徑")

    # =======================================================================================================
    
    # 交換模式
    # 開立發票xml存放路徑
    output_dir_A0101 = models.CharField(max_length=255, blank=True, null=True, verbose_name="A0101 輸出路徑")
    
    # 交換模式
    # 接收發票xml存放路徑
    output_dir_A0102 = models.CharField(max_length=255, blank=True, null=True, verbose_name="A0102 接收路徑")

    # 交換模式    
    # 作廢發票xml存放路徑
    output_dir_A0201 = models.CharField(max_length=255, blank=True, null=True, verbose_name="A0201 輸出路徑")

    # 交換模式
    # 作廢發票確認xml存放路徑
    output_dir_A0202 = models.CharField(max_length=255, blank=True, null=True, verbose_name="A0202 接收路徑")

    # 交換模式
    # 退回發票xml存放路徑
    output_dir_A0301 = models.CharField(max_length=255, blank=True, null=True, verbose_name="A0301 輸出路徑")

    # 交換模式
    # 退回發票確認xml存放路徑
    output_dir_A0302 = models.CharField(max_length=255, blank=True, null=True, verbose_name="A0302 接收路徑")

    # 交換模式
    # 開立折讓單xml存放路徑
    output_dir_B0101 = models.CharField(max_length=255, blank=True, null=True, verbose_name="B0101 輸出路徑")

    # 交換模式    
    # 接收折讓單xml存放路徑
    output_dir_B0102 = models.CharField(max_length=255, blank=True, null=True, verbose_name="B0102 接收路徑")

    # 交換模式
    # 作廢折讓單xml存放路徑
    output_dir_B0201 = models.CharField(max_length=255, blank=True, null=True, verbose_name="B0201 輸出路徑")

    # 交換模式
    # 作廢折讓單確認xml存放路徑
    output_dir_B0202 = models.CharField(max_length=255, blank=True, null=True, verbose_name="B0202 接收路徑")

    # =======================================================================================================

    # 總、分支機構配號檔存放路徑
    output_dir_E0401 = models.CharField(max_length=255, blank=True, null=True, verbose_name="E0401 輸出路徑")

    # 空白未使用字軌配號檔存放路徑
    output_dir_E0402 = models.CharField(max_length=255, blank=True, null=True, verbose_name="E0402 輸出路徑")

    # 營業人電子發票配號檔存放路徑
    input_dir_E0501 = models.CharField(max_length=255, blank=True, null=True, verbose_name="E0501 接收路徑")

    # 營業人進項存證發票檔存放路徑
    input_dir_E0502 = models.CharField(max_length=255, blank=True, null=True, verbose_name="E0502 接收路徑")

    # 營業人進項存證折讓證明單檔存放路徑
    input_dir_E0503 = models.CharField(max_length=255, blank=True, null=True, verbose_name="E0503 接收路徑")

    # 中獎清冊資料檔
    output_dir_E0504 = models.CharField(max_length=255, blank=True, null=True, verbose_name="E0504 接收路徑")

    # 稅局回覆檔案路徑
    input_dir_ProcessResult = models.CharField(max_length=255, blank=True, null=True, verbose_name="ProcessResult 接收路徑")

    # =======================================================================================================
     
    output_dir_invoice_heatsense_paper = models.CharField(max_length=255, blank=True, null=True, verbose_name="感熱紙發票 輸出路徑")
    output_dir_invoice_A4_paper = models.CharField(max_length=255, blank=True, null=True, verbose_name="A4發票 輸出路徑")
    output_dir_allowance_A4_paper = models.CharField(max_length=255, blank=True, null=True, verbose_name="A4折讓單 輸出路徑")
    AES_KEY = models.CharField(max_length=255, blank=True, null=True, verbose_name="ASE_KEY")
    aes_key_last_updated = models.DateField(null=True, blank=True, verbose_name="ASE_KEY 最後更新日期")




    class Meta:
        verbose_name = "公司通知設定"
        verbose_name_plural = "公司通知設定"
        ordering = ['company']

    def __str__(self):
        return f"{self.company.company_id} 通知設定"

    
class SystemConfig(models.Model):
    email_validator = RegexValidator(
        regex=r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$',
        message='請輸入有效的電子郵件格式'
    )

    operator_output_email_address = models.CharField(
        max_length=100,
        validators=[email_validator],
        blank=True,
        null=True,
        verbose_name="操作人員通知 Email"
    )

    F0401_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="F0401 XSD 路徑")
    
    F0501_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="F0501 XSD 路徑")
    
    G0401_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="G0401 XSD 路徑")
    
    G0501_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="G0501 XSD 路徑")
    
    A0101_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="A0101 XSD 路徑")
    A0102_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="A0102 XSD 路徑")

    A0201_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="A0201 XSD 路徑")
    A0202_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="A0202 XSD 路徑")

    A0301_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="A0301 XSD 路徑")
    A0302_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="A0302 XSD 路徑")

    B0101_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="B0101 XSD 路徑")
    B0102_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="B0102 XSD 路徑")

    B0201_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="B0201 XSD 路徑")
    B0202_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="B0202 XSD 路徑")

    E0401_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="E0401 XSD 路徑")

    E0402_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="E0402 XSD 路徑")

    E0501_XSD_path = models.CharField(max_length=255, blank=True, null=True, verbose_name="E0501 XSD 路徑")


    class Meta:
        verbose_name = "全域系統設定"
        verbose_name_plural = "全域系統設定"

    def __str__(self):
        return "系統設定"
