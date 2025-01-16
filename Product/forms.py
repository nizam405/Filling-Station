from django import forms
import datetime
from .models import Sell, Purchase, StorageReading, SellingRate, PurchaseRate, Stock, InitialStock
from Core.widgets import SelectProduct
from Core.functions import year_choices
from Core.functions import account_start_date

# Daily Transactions
class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['product','quantity','purchase_rate']
        widgets = {'product': SelectProduct}

class SellForm(forms.ModelForm):
    class Meta:
        model = Sell
        fields = ['product','quantity','selling_rate']
        widgets = {'product': SelectProduct}

class StorageReadingForm(forms.ModelForm):
    class Meta:
        model = StorageReading
        fields = ['date', 'product', 'tank_deep', 'lorry_load']
        widgets = {
            'product': SelectProduct,
            'date': forms.SelectDateWidget(years=year_choices()),
            }

# Rates
class PurchaseRateForm(forms.ModelForm):
    class Meta:
        model = PurchaseRate
        fields = ['date','variant','amount']
        widgets = {
            'date': forms.SelectDateWidget(years=year_choices()),
            }

class SellingRateForm(forms.ModelForm):
    class Meta:
        model = SellingRate
        fields = ['date','variant','amount']
        widgets = {
            'date': forms.SelectDateWidget(years=year_choices()),
            }

# Ledger Forms
class ProductLedgerFilterForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['date','product']
        widgets = {
            'date': forms.SelectDateWidget(
                years=range(account_start_date().year,datetime.date.today().year+1)
            )
        }

class InitialStockForm(forms.ModelForm):
    class Meta:
        model = InitialStock
        fields = ['product','quantity','purchase_rate']
        widgets = {'product': SelectProduct}