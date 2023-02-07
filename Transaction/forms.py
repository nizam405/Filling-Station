from django import forms
from datetime import date
from .models import CashBalance

class DateForm(forms.Form):
    balance_date = CashBalance.objects.first()
    if not balance_date:
        balance_date = date.today()
    else: balance_date = balance_date.date
    date = forms.DateField(widget=forms.SelectDateWidget(
        years=range(balance_date.year, date.today().year+1)))

class CashBalanceForm(forms.ModelForm):

    class Meta:
        model = CashBalance
        fields = '__all__'
        # widgets = {
        #     'date': forms.DateInput(attrs={'type':'date'})
        # }

class CashBalanceForm2(forms.ModelForm):
    balance_form = forms.BooleanField(widget=forms.HiddenInput,initial=True)

    class Meta:
        model = CashBalance
        fields = '__all__'
        widgets = {
            'date': forms.HiddenInput(),
            'amount': forms.HiddenInput()
        }
