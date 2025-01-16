from django import forms
from .models import Withdraw, Investment, OwnersEquity, FixedAsset
from Core.functions import year_choices
from Core.choices import balance_years

class WithdrawFilterForm(forms.ModelForm):
    class Meta:
        model = Withdraw
        fields = ['date','owner']
        widgets = {'date': forms.SelectDateWidget}

# class InvestmentForm(forms.ModelForm):
#     class Meta:
#         model = Investment
#         fields = '__all__'
#         widgets = {
#             'date': forms.SelectDateWidget(
#                 attrs={'disabled': 'disabled'}  # Disable the date field
#             ),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super(InvestmentForm, self).__init__(*args, **kwargs)
#         self.fields['date'].required = False

# Detail view
class OwnersEquityDetailFilter(forms.ModelForm):
    class Meta:
        model = OwnersEquity
        fields = ['owner', 'date']
        widgets = {'date': forms.SelectDateWidget(
            years=[year[0] for year in balance_years()]
        )}

# Top Sheet Filter
class OwnersEquityFilter(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OwnersEquityFilter, self).__init__(*args, **kwargs)
        self.fields['owner'].required = False
        
    class Meta:
        model = OwnersEquity
        fields = ['owner', 'year']
        widgets = {'year': forms.Select(choices=balance_years())}

class FixedAssetForm(forms.ModelForm):
    class Meta:
        model = FixedAsset
        fields = '__all__'
        widgets = {'date': forms.SelectDateWidget(years=year_choices())}
