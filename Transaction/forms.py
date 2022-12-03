from django import forms

class DateForm(forms.Form):
    # date = forms.DateField(widget=forms.DateInput(format="%d/%m/%Y",attrs={'type':'date'}))
    date = forms.DateField(widget=forms.SelectDateWidget)