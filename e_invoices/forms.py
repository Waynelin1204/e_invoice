from django import forms
from e_invoices.models import NumberDistribution

class NumberDistributionForm(forms.ModelForm):
    class Meta:
        model = NumberDistribution
        fields = ['company', 'initial_char', 'period', 'start_number', 'end_number', 'status']
        widgets = {
            'company': forms.Select(attrs={'class': 'form-control'}),
            'initial_char': forms.TextInput(attrs={'class': 'form-control'}),
            'period': forms.TextInput(attrs={'class': 'form-control'}),
            'start_number': forms.TextInput(attrs={'class': 'form-control'}),
            'end_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_period(self):
        period = self.cleaned_data.get('period')
        if len(period) < 5:  # 假設最小長度是5
            raise forms.ValidationError("期別長度太短，請檢查。ex: 11403")
        return period
    
    def clean_start_number(self):
        start_number = self.cleaned_data.get('start_number')
        if len(start_number) < 8:  # 假設最小長度是8
            raise forms.ValidationError("起始號碼長度太短，請檢查。")
        return start_number
    
    def clean_end_number(self):
        end_number = self.cleaned_data.get('end_number')
        if len(end_number) < 8:  # 假設最小長度是5
            raise forms.ValidationError("結束號碼長度太短，請檢查。")
        return end_number
    
    def clean(self):
        cleaned_data = super().clean()
        start_number = cleaned_data.get("start_number")
        end_number = cleaned_data.get("end_number")

        # 如果存在這些欄位並且結束號碼小於起始號碼
        if start_number and end_number:
            try:
                # 轉換為整數進行比較
                start_number = int(start_number)
                end_number = int(end_number)
                
                if end_number < start_number:
                    raise forms.ValidationError("結束號碼不能小於起始號碼。")
            except ValueError:
                raise forms.ValidationError("號碼必須為有效的數字。")
        
        return cleaned_data