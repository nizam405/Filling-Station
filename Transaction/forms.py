from django import forms
from datetime import date
from .models import CashBalance
from Core.functions import year_choices
from .functions import first_balance_date

class CashBalanceForm(forms.ModelForm):

    class Meta:
        model = CashBalance
        fields = '__all__'
        widgets = {
            'date': forms.SelectDateWidget(years=year_choices())
        }

# DailyTransactionView
class CashBalanceForm2(forms.ModelForm):
    # balance_form = forms.BooleanField(widget=forms.HiddenInput,initial=True)
    balance_cf = forms.FloatField(widget=forms.HiddenInput)

    class Meta:
        model = CashBalance
        fields = ['amount','balance_cf']
        # widgets = {
        #     'date': forms.HiddenInput(attrs={'name':'next_date'}),
        #     'amount': forms.HiddenInput()
        # }

# Multiple Action
class CashBalanceControlForm(forms.Form):
    balance_date = first_balance_date()
    if not balance_date: balance_date = date.today()

    from_date = forms.DateField(label="তারিখ (হতে)",
        widget=forms.SelectDateWidget( years=range(balance_date.year, date.today().year+2)))
    to_date = forms.DateField(label="তারিখ (পর্যন্ত)",
        widget=forms.SelectDateWidget(years=range(balance_date.year, date.today().year+2)))
    action = forms.ChoiceField(choices=[('save','Save'),('delete','Delete')])
