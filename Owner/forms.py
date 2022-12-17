from django import forms
from .models import Withdraw, Investment

class WithdrawForm(forms.ModelForm):
    class Meta:
        model = Withdraw
        fields = '__all__'
        widgets = {'date': forms.SelectDateWidget}

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = '__all__'
        widgets = {'date': forms.SelectDateWidget}