from django import forms
from .models import Withdraw, Investment, OwnersEquity, FixedAsset
from Owner.models import Owner
from Core.choices import year_choices

class WithdrawForm(forms.ModelForm):
    class Meta:
        model = Withdraw
        fields = '__all__'
        widgets = {'date': forms.HiddenInput}

class InvestmentForm(forms.ModelForm):
    class Meta:
        model = Investment
        fields = '__all__'
        widgets = {'date': forms.SelectDateWidget(years=year_choices())}

# Detail view
class OwnersEquityForm(forms.ModelForm):
    class Meta:
        model = OwnersEquity
        fields = ['owner', 'month', 'year']
    
    owner = forms.ModelChoiceField(queryset=Owner.objects.all(), empty_label=None)

# Top Sheet Filter
class OwnersEquityFilter(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(OwnersEquityFilter, self).__init__(*args, **kwargs)
        self.fields['owner'].required = False
        
    class Meta:
        model = OwnersEquity
        fields = ['owner', 'year']

class FixedAssetForm(forms.ModelForm):
    class Meta:
        model = FixedAsset
        fields = '__all__'
        widgets = {'date': forms.SelectDateWidget(years=year_choices())}
