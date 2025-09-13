from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

class ChangeDefaultPasswordForm(forms.Form):
    new_password = forms.CharField(
        label="كلمة المرور الجديدة",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور الجديدة',
            'id': 'new_password'
        }),
        min_length=8
    )
    
    confirm_password = forms.CharField(
        label="تأكيد كلمة المرور",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أعد إدخال كلمة المرور الجديدة',
            'id': 'confirm_password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and new_password != confirm_password:
            raise ValidationError("كلمة المرور الجديدة وتأكيدها غير متطابقين")

        return cleaned_data