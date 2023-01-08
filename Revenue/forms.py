from django import forms
from .models import Revenue

class RevenueForm(forms.ModelForm):
    class Meta:
        model = Revenue
        fields = '__all__'
        widgets = {'date': forms.HiddenInput}