from django import forms
from .models import Sell, Purchase

# class SellForm(forms.ModelForm):
#     class Meta:
#         model = Sell
#         fields = '__all__'
#         widgets = {'date': forms.SelectDateWidget}
        
# class PurchaseForm(forms.ModelForm):
#     class Meta:
#         model = Purchase
#         fields = '__all__'
#         widgets = {'date': forms.SelectDateWidget}    

    # def __init__(self, *args, **kwargs):
    #     date = kwargs.pop('date')
    #     super(PurchaseForm, self).__init__(*args, **kwargs)
    #     self.fields['date'].initial = date

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = '__all__'
        widgets = {
            'date': forms.HiddenInput,
            }

class SellForm(forms.ModelForm):
    class Meta:
        model = Sell
        fields = '__all__'
        widgets = {
            'date': forms.HiddenInput,
            }