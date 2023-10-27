from django import forms
from datetime import date
from .models import CashBalance
from Core.choices import year_choices
from .functions import first_balance_date, last_balance_date

class DateForm(forms.Form):
    from_date = first_balance_date()
    if not from_date: from_date = date.today()
    date = forms.DateField(widget=forms.SelectDateWidget(
        years=range(from_date.year, date.today().year+1)))

# CreateView
class CashBalanceForm(forms.ModelForm):

    class Meta:
        model = CashBalance
        fields = '__all__'
        widgets = {
            'date': forms.SelectDateWidget(years=year_choices())
        }

# DailyTransactionView
class CashBalanceForm2(forms.ModelForm):
    balance_form = forms.BooleanField(widget=forms.HiddenInput,initial=True)

    class Meta:
        model = CashBalance
        fields = '__all__'
        widgets = {
            'date': forms.HiddenInput(),
            'amount': forms.HiddenInput()
        }

# Multiple Action
class CashBalanceControlForm(forms.Form):
    balance_date = first_balance_date()
    if not balance_date: balance_date = date.today()

    from_date = forms.DateField(label="তারিখ (হতে)",
        widget=forms.SelectDateWidget( years=range(balance_date.year, date.today().year+2)))
    to_date = forms.DateField(label="তারিখ (পর্যন্ত)",
        widget=forms.SelectDateWidget(years=range(balance_date.year, date.today().year+2)))
    action = forms.ChoiceField(choices=[('save','Save'),('delete','Delete')])
