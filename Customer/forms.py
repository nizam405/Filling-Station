from django import forms
from Core.widgets import SelectProduct, SelectCustomer
from .models import DueSell, DueCollection, Customer

class DueSellForm(forms.ModelForm):
    class Meta:
        model = DueSell
        fields = '__all__'
        widgets = {
            'product': SelectProduct,
            'date': forms.HiddenInput
            }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(active=True).order_by('cust_type','group','name')

class DueCollectionForm(forms.ModelForm):
    class Meta:
        model = DueCollection
        fields = '__all__'
        widgets = {
            'date': forms.HiddenInput,
            'customer': SelectCustomer
            }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.filter(active=True).order_by('cust_type','group','name')


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name','short_name','cust_type','group','mobile','serial']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['serial'] = self.instance.get_next_serial()