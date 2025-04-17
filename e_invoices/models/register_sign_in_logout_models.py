from django  import forms
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    company = models.ForeignKey("e_invoices.Company", on_delete=models.CASCADE, related_name="users")  # 所屬公司
    #company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)  # or use `null=False` if mandatory
    viewable_companies = models.ManyToManyField("e_invoices.Company", related_name="viewable_by_users")  # 可查看的公司


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