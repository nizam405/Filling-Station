from django import forms
from .choices import MONTHS, YEAR
from .models import CustomerBalance, GroupofCompanyBalance
# from Customer.models import Customer

# class FilterForm(forms.Form):
#     qs = Customer.objects.filter(cust_type='Individual')
#     customer = forms.ModelChoiceField(queryset=qs,label="পার্টি")
#     month = forms.CharField(widget=forms.Select(choices=MONTHS), label="মাস")
#     year = forms.CharField(widget=forms.Select(choices=YEAR), label="বছর")

class CustomerLedgerFilterForm(forms.ModelForm):
    class Meta:
        model = CustomerBalance
        fields = ['customer','month','year']