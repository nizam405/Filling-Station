from django import forms
from .choices import MONTHS, YEAR
from .models import CustomerBalance, GroupofCompanyBalance, Storage
# from Customer.models import Customer

# class FilterForm(forms.Form):
#     qs = Customer.objects.filter(cust_type='Individual')
#     customer = forms.ModelChoiceField(queryset=qs,label="পার্টি")
#     month = forms.CharField(widget=forms.Select(choices=MONTHS), label="মাস")
#     year = forms.CharField(widget=forms.Select(choices=YEAR), label="বছর")

# Used in Customer Ledger
class CustomerLedgerFilterForm(forms.ModelForm):
    class Meta:
        model = CustomerBalance
        fields = ['customer','month','year']

# Used in Group of company Ledger
class GroupofCompanyLedgerFilterForm(forms.ModelForm):
    class Meta:
        model = GroupofCompanyBalance
        fields = ['customer','month','year']

# Used on several pages to filter
class DateFilterForm(forms.Form):
    month = forms.ChoiceField(choices=MONTHS, label="মাস")
    year = forms.ChoiceField(choices=YEAR, label="বছর")

# Used in Product Ledger
class StorageFilterForm(forms.ModelForm):
    class Meta:
        model = Storage
        fields = ['product','month','year']