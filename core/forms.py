from django import forms
from datetime import date
from .models import Settings

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = '__all__'
        widgets = {
            'start_date': forms.SelectDateWidget()
        }