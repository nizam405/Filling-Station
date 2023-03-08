from django import forms
from .choices import MONTHS, YEAR
# from Customer.choices import customerDueChoice
from .models import CustomerBalance, GroupofCompanyBalance, Storage, BadDebt
from Core.widgets import SelectCustomer
# from Customer.models import Customer
# from django.db.models import Q

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

class BadDebtForm(forms.ModelForm):
    disable_customer = forms.BooleanField(
        required=False, label="পার্টি নিষ্ক্রিয় করুন",
        widget=forms.CheckboxInput())
    class Meta:
        model = BadDebt
        # fields = '__all__'
        fields = ['month','year','customer','amount', 'disable_customer']
        widgets = {'customer':SelectCustomer}