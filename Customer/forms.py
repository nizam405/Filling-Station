from django import forms
from .models import DueSell, DueCollection, Customer

class DueSellForm(forms.ModelForm):
    class Meta:
        model = DueSell
        fields = '__all__'
        widgets = {'date': forms.HiddenInput}
        # widgets = {'date': forms.SelectDateWidget}

class DueCollectionForm(forms.ModelForm):
    class Meta:
        model = DueCollection
        fields = '__all__'
        widgets = {'date': forms.HiddenInput}
        # widgets = {'date': forms.SelectDateWidget}

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'