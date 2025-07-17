from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label="使用者名稱",
        max_length=150,
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'class': 'form-control',
            'placeholder': '請輸入帳號'
        })
    )
    password = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'placeholder': '請輸入密碼'
        })
    )

