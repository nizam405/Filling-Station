from django import forms
from .models import Expenditure

class ExpenditureForm(forms.ModelForm):
    class Meta:
        model = Expenditure
        fields = '__all__'
        widgets = {'date': forms.SelectDateWidget}