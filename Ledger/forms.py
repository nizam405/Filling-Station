from django import forms
from .models import CustomerBalance, GroupofCompanyBalance, Storage
from Customer.models import Customer, GroupofCompany

# Used in Customer Ledger
class CustomerLedgerFilterForm(forms.ModelForm):
    class Meta:
        model = CustomerBalance
        fields = ['customer','month','year']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(
            customerbalance__bad_debt=False, active=True
        ).distinct()

# Used in Group of company Ledger
class GroupofCompanyLedgerFilterForm(forms.ModelForm):
    class Meta:
        model = GroupofCompanyBalance
        fields = ['customer','month','year']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = GroupofCompany.objects.filter(
            groupofcompanybalance__bad_debt=False, active=True
        ).distinct()

class CustomerBalanceForm(forms.ModelForm):
    class Meta:
        model = CustomerBalance
        fields = ['customer','amount','bad_debt']
    
    def __init__(self, *args, **kwargs):
        super(CustomerBalanceForm, self).__init__(*args, **kwargs)
        # Disable the customer field
        self.fields['customer'].disabled = True
    
class GroupofCompanyBalanceForm(forms.ModelForm):
    class Meta:
        model = GroupofCompanyBalance
        fields = ['customer','amount','bad_debt']
    
    def __init__(self, *args, **kwargs):
        super(GroupofCompanyBalanceForm, self).__init__(*args, **kwargs)
        # Disable the customer field
        self.fields['customer'].disabled = True

# Used in Product Ledger
class StorageFilterForm(forms.ModelForm):
    class Meta:
        model = Storage
        fields = ['product','month','year']

