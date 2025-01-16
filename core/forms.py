from django import forms
import datetime

from .models import Settings
from Transaction.functions import first_balance_date

class DateForm(forms.Form):
    from_date = first_balance_date()
    print(from_date)
    date = forms.DateField(widget=forms.SelectDateWidget(
        years=range(from_date.year, datetime.date.today().year+1)))

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = '__all__'
        widgets = {
            'start_date': forms.SelectDateWidget(
                years=range(2000,datetime.date.today().year+1)
            )
        }