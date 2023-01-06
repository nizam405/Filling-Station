from django import forms
from datetime import date

MONTHS = [
    ('1', 'জানুয়ারি'),
    ('2', 'ফেব্রুয়ারি'),
    ('3', 'মার্চ'),
    ('4', 'এপ্রিল'),
    ('5', 'মে'),
    ('6', 'জুন'),
    ('7', 'জুলাই'),
    ('8', 'আগস্ট'),
    ('9', 'সেপ্টেম্বর'),
    ('10', 'অক্টোবর'),
    ('11', 'নভেম্বর'),
    ('12', 'ডিসেম্বর'),
]

curentYear = date.today().year+1
YEAR = [(i,i) for i in range(2022, curentYear)]

class MonthForm(forms.Form):
    month = forms.Select(choices=MONTHS)
    year = forms.Select(choices=YEAR)