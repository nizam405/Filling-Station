from django import forms
from .models import CashBalance
from datetime import date
from .models import CashBalance

class DateForm(forms.Form):
    balance_date = CashBalance.objects.first().date
    today = date.today()
    date = forms.DateField(widget=forms.SelectDateWidget(
        years=range(balance_date.year, date.today().year+1),
        months={
            balance_date.month:balance_date.strftime("%b"),
            today.month: today.strftime("%b")}))

class CashBalanceForm(forms.ModelForm):

    class Meta:
        model = CashBalance
        fields = '__all__'
        widgets = {
            'date': forms.SelectDateWidget()
        }

class CashBalanceForm2(forms.ModelForm):

    class Meta:
        model = CashBalance
        fields = '__all__'
        widgets = {
            'date': forms.HiddenInput(),
            'amount': forms.HiddenInput()
        }
