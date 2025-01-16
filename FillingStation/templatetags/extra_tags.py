from django import template
from django.template.defaultfilters import floatformat
import datetime
import pybengali
from Core.choices import MONTHS

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
    nums = [i for i in range(0,len(formset))]
    return zip(formset,nums)

@register.filter(name='e2b_digit')
def number_in_bangla(number):
    return pybengali.convert_e2b_digit(number)

@register.filter
def format_num(value,decimal_places=3):
    if value != None:
        return price_separate(number_in_bangla(floatformat(value,decimal_places)))
    else: return ""

@register.filter
def format_currency(value,decimal_places=2):
    if value != None:
        return "৳ "+price_separate(number_in_bangla(floatformat(value,decimal_places)))
    else: return ""

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
            return f"{d}-{ms}-{y[2:]}"
        return f"{m}-{d}, {y}"
    else: return ""

@register.filter(name='absolute')
def absolute(value):
    return abs(value)

@register.filter(name='mul')
def mul(value1,value2):
    if value1 is None or value2 is None:
        return 0
    else:
        return value1*value2

@register.filter(name='sub')
def sub(value1,value2):
    if value1 is None or value2 is None:
        return 0
    else:
        return value1-value2

@register.filter(name='pages')
def pages(current,max):
    display = 15
    first = 1 if current < display//2 else current - display//2
    last = display if current < display//2 else current + display//2
    if last > max:
        first -= last-max
        last = max
    # print(current,max,first,last)
    return range(first,last+1)

@register.filter(name='neg')
def neg(val): return -val

@register.filter
def skip_none(value):
    if value: return value
    else: return ''

@register.filter
def skip_zero(value):
    if value and value != 0: return value
    else: return None