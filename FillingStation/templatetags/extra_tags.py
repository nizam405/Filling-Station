from django import template
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
        return price
    rev = sign + new_str[::-1]
    return rev

@register.filter(name='zip')
def zip_lists(object_list):
    nums = [i for i in range(1,object_list.count()+1)]
    return zip(object_list,nums)

@register.filter(name='formsetNumber')
def formset_number(formset):
    print(len(formset))
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
def convert_date_ban(date):
    d = pybengali.convert_e2b_digit(date.day)
    m = MONTHS[date.month-1][1]
    y = pybengali.convert_e2b_digit(date.year)
    return f"{m} - {d}, {y}"