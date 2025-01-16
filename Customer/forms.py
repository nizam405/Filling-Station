from django import forms
from Core.widgets import SelectProduct
from .models import DueSell, Customer
from Customer.models import Customer, GroupofCompany, CustomerDue, GroupofCompanyDue

class DueSellForm(forms.ModelForm):
    # add_to_sell = forms.BooleanField(label='বিক্রয়ে যুক্ত করুন',required=False)
    class Meta:
        model = DueSell
        fields = ['customer','product','quantity','selling_rate']
        widgets = {
            'product': SelectProduct,
            # 'add_to_sell': forms.CheckboxInput
            }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(active=True).order_by('cust_type','group','name')

# class DueCollectionForm(forms.ModelForm):
#     class Meta:
#         model = DueCollection
#         fields = '__all__'
#         widgets = {
#             'date': forms.HiddenInput,
#             'customer': SelectCustomer
#         }
        
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['customer'].queryset = Customer.objects.filter(active=True).order_by('cust_type','group','name')


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name','short_name','cust_type','group','mobile','serial']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['serial'] = self.instance.get_next_serial()

# Used in Customer Ledger
class CustomerLedgerFilterForm(forms.ModelForm):
    class Meta:
        model = CustomerDue
        fields = ['date','customer']
        widgets = {
            'date': forms.SelectDateWidget
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(
            customerdue__bad_debt=False, active=True
        ).distinct()

# Used in Group of company Ledger
class GroupofCompanyLedgerFilterForm(forms.ModelForm):
    class Meta:
        model = GroupofCompanyDue
        fields = ['customer','date']
        widgets = {
            'date': forms.SelectDateWidget
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = GroupofCompany.objects.filter(
            groupofcompanybalance__bad_debt=False, active=True
        ).distinct()

class CustomerDueForm(forms.ModelForm):
    class Meta:
        model = CustomerDue
        fields = ['customer','amount','bad_debt']
    
    def __init__(self, *args, **kwargs):
        super(CustomerDueForm, self).__init__(*args, **kwargs)
        # Disable the customer field
        self.fields['customer'].disabled = True
    
class GroupofCompanyDueForm(forms.ModelForm):
    class Meta:
        model = GroupofCompanyDue
        fields = ['customer','amount','bad_debt']
    
    def __init__(self, *args, **kwargs):
        super(GroupofCompanyDueForm, self).__init__(*args, **kwargs)
        # Disable the customer field
        self.fields['customer'].disabled = True