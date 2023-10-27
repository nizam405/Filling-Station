from django import forms
from .models import Sell, Purchase, StorageReading, Rate
from Core.widgets import SelectProduct
from Core.choices import year_choices

class PurchaseForm(forms.ModelForm):
    update_rate = forms.BooleanField(label="দর পরিবর্তন", required=False)
    class Meta:
        model = Purchase
        fields = ['product','quantity','rate','amount','update_rate']
        widgets = {
            'product': SelectProduct,
            # 'date': forms.HiddenInput,
            }

class SellForm(forms.ModelForm):
    update_rate = forms.BooleanField(label="দর পরিবর্তন", required=False)
    class Meta:
        model = Sell
        fields = ['product','quantity','rate','amount','update_rate']
        widgets = {
            'product': SelectProduct,
            # 'date': forms.HiddenInput,
            }

class StorageReadingForm(forms.ModelForm):
    class Meta:
        model = StorageReading
        fields = '__all__'
        widgets = {
            'product': SelectProduct,
            'date': forms.SelectDateWidget(years=year_choices()),
            }

class RateForm(forms.ModelForm):
    class Meta:
        model = Rate
        fields = ['date','purchase_rate','selling_rate']
        widgets = {
            'date': forms.SelectDateWidget(years=year_choices()),
            }