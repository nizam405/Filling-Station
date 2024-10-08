from django import forms
from .choices import MONTHS, YEAR
from .models import CustomerBalance, GroupofCompanyBalance, Storage
from Customer.models import Customer, GroupofCompany
from Core.widgets import SelectCustomer

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

# Used on several pages to filter
class DateFilterForm(forms.Form):
    month = forms.ChoiceField(choices=MONTHS, label="মাস")
    year = forms.ChoiceField(choices=YEAR, label="বছর")

# Used in Product Ledger
class StorageFilterForm(forms.ModelForm):
    class Meta:
        model = Storage
        fields = ['product','month','year']

# Used in Storage Update Formset
class StorageUpdateForm(forms.ModelForm):
    class Meta:
        model = Storage
        fields = ['product','quantity','price']
    
    def __init__(self, *args, **kwargs):
        super(StorageUpdateForm, self).__init__(*args, **kwargs)
        # Disable the product field
        self.fields['product'].disabled = True
