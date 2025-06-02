from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class CustomRegisterForm(UserCreationForm):
    username = forms.CharField(
        label="使用者名稱",
        error_messages={
            "required": "請輸入使用者名稱",
            "unique": "此使用者名稱已被使用",
        }
    )
    email = forms.EmailField(
        label="電子郵件",
        required=True,
        error_messages={
            "required": "請輸入電子郵件",
            "invalid": "請輸入正確的電子郵件格式",
        }
    )
    password1 = forms.CharField(
        label="密碼",
        widget=forms.PasswordInput,
        error_messages={
            "required": "請輸入密碼"
        }
    )
    password2 = forms.CharField(
        label="確認密碼",
        widget=forms.PasswordInput,
        error_messages={
            "required": "請再次輸入密碼"
        }
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("兩次輸入的密碼不一致")
        return password2

    def _post_clean(self):
        super()._post_clean()
        # 自訂 password validator 錯誤訊息翻譯
        password = self.cleaned_data.get('password1')
        if password:
            try:
                # 傳 self.instance 即可，不需先使用 username
                validate_password(password, self.instance)
            except ValidationError as e:
                translated_errors = []
                for error in e.messages:
                    if "This password is too short. It must contain at least 8 characters." in error:
                        translated_errors.append("密碼太短，至少需要 8 個字元。")
                    elif "This password is too common" in error:
                        translated_errors.append("這個密碼太常見，請換一個更安全的密碼。")
                    elif "This password is entirely numeric" in error:
                        translated_errors.append("密碼不能全為數字。")
                    else:
                        translated_errors.append(error)
                self.add_error('password1', translated_errors)
