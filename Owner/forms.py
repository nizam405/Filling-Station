from django import forms
from .models import Withdraw, Investment, OwnersEquity
from Core.choices import year_choices

class WithdrawForm(forms.ModelForm):
    class Meta:
        model = Withdraw
        fields = '__all__'
        widgets = {'date': forms.HiddenInput}
        # widgets = {'date': forms.SelectDateWidget}

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = '__all__'
        widgets = {'date': forms.SelectDateWidget(years=year_choices())}

class OwnersEquityForm(forms.ModelForm):
    class Meta:
        model = OwnersEquity
        fields = ['owner', 'month', 'year']