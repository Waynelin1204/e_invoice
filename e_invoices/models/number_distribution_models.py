from django  import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError


from django.db import models
class NumberDistribution(models.Model):
    company = models.ForeignKey("e_invoices.Company", on_delete=models.CASCADE, related_name='number_distributions')
    initial_char = models.CharField(max_length=2)  # 開頭字母
    period = models.CharField(max_length=5)  # 期別
    start_number = models.CharField(max_length=8) # 起始號碼
    end_number = models.CharField(max_length=8) # 結束號碼
    invoice_type = models.CharField(max_length=2) # 07 or 08
    current_number = models.CharField(max_length=8, blank=True, null=True)  # 當前號碼
    last_used_date = models.DateField(blank=True, null=True)  # 最後使用日期
    status = models.CharField(max_length=10, choices=[('available', 'Available'), ('uploaded', 'Uploaded')], default='available')

    def __str__(self):
        return f"{self.company}"