from django import forms
from .models import Sell, Purchase, StorageReading
from Core.widgets import SelectProduct

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = '__all__'
        widgets = {
            'product': SelectProduct,
            'date': forms.HiddenInput,
            }

class SellForm(forms.ModelForm):
    class Meta:
        model = Sell
        fields = '__all__'
        widgets = {
            'product': SelectProduct,
            'date': forms.HiddenInput,
            }

class StorageReadingForm(forms.ModelForm):
    class Meta:
        model = StorageReading
        fields = '__all__'
        widgets = {
            'product': SelectProduct,
            'date': forms.SelectDateWidget,
            }