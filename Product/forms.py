from django import forms
from .models import Sell, Purchase

class SellForm(forms.ModelForm):
    class Meta:
        model = Sell
        fields = '__all__'
        widgets = {'date': forms.SelectDateWidget}
        
class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = '__all__'
        widgets = {'date': forms.SelectDateWidget}