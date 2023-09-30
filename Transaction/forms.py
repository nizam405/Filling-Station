from django import forms
from datetime import date
from .models import CashBalance
from Core.choices import year_choices

class DateForm(forms.Form):
    first_balance = CashBalance.objects.first()
    if first_balance:
        balance_date = first_balance.date
    else:
        balance_date = date.today()
    date = forms.DateField(widget=forms.SelectDateWidget(
        years=range(balance_date.year, date.today().year+1)))

class CashBalanceForm(forms.ModelForm):

    class Meta:
        model = CashBalance
        fields = '__all__'
        widgets = {
            'date': forms.SelectDateWidget(years=year_choices())
        }

class CashBalanceForm2(forms.ModelForm):
    balance_form = forms.BooleanField(widget=forms.HiddenInput,initial=True)

    class Meta:
        model = CashBalance
        fields = '__all__'
        widgets = {
            'date': forms.HiddenInput(),
            'amount': forms.HiddenInput()
        }
