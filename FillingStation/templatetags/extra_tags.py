from django import template
import datetime
import pybengali
from Ledger.choices import MONTHS

register = template.Library()

@register.filter(name="ezynumber")
def price_separate(price):
    new_str = ""
    if price != '' and str(price)[0] == '-':
        sign = '-'  
        price = str(price)[1:]
    else: 
        sign = ""
        price = str(price)
    price_str = price[::-1]
    if '.' in price_str:
        indx = price_str.index('.')+1
        new_str += price_str[0:indx]
        price_str = price_str[indx:]
    length = len(price_str)
    if length > 3:
        new_str += price_str[0:3] + "," + price_str[3]
        if length == 5: new_str += price_str[4]
        if length > 5:
            new_str += price_str[4] + "," + price_str[5]
            if length == 7: new_str += price_str[6]
            if length > 7:
                new_str += price_str[6] + "," + price_str[7:]
    else:
        return sign + price
    rev = sign + new_str[::-1]
    return rev

@register.filter(name='zip')
def zip_lists(object_list,last=0):
    start=last+1
    nums = [i for i in range(start,len(object_list)+start)]
    return zip(object_list,nums)

@register.filter(name='formsetNumber')
def formset_number(formset):
    # print(len(formset))
    nums = [i for i in range(0,len(formset))]
    return zip(formset,nums)

@register.filter(name='e2b_digit')
def number_in_bangla(number):
    return pybengali.convert_e2b_digit(number)

@register.filter(name='e2b_month')
def month_in_bangla(number):
    month = MONTHS[int(number)-1]
    return month[1]

@register.filter(name="e2b_date")
def convert_date_ban(date,short=False):

    if isinstance(date, datetime.date):
        d = pybengali.convert_e2b_digit(date.day)
        m = MONTHS[date.month-1][1]
        ms = pybengali.convert_e2b_digit(MONTHS[date.month-1][0])
        y = pybengali.convert_e2b_digit(date.year)
        if short:
            return f"{d}/{ms}/{y[2:]}"
        return f"{m}-{d}, {y}"
    else: return ""

@register.filter(name='absolute')
def absolute(value):
    return abs(value)