from django  import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.db import models

class UploadLog(models.Model):
    company_id = models.CharField(max_length=10, null=True)  # 營業人代碼

    import_type = models.CharField(
        max_length=10,
        choices=[('invoice', 'invoice'), ('allowance', 'allowance')],  # 匯入類型
    )
    
    business_type = models.CharField(
        max_length=3,
        choices=[('B2B', 'B2B'), ('B2C', 'B2C')],  # 商業類型
    )

    file_name = models.CharField(max_length=255)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    error_excel_path = models.TextField(null=True, blank=True)
    upload_user = models.CharField(max_length=150)
    upload_time = models.DateTimeField()