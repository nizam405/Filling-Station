from .models import CashBalance
from datetime import timedelta

def last_balance_date():
    obj = CashBalance.objects.order_by('-date').first()
    return obj.date

def next_to_last_balance_date():
    last = last_balance_date()
    return last + timedelta(days=1)

def get_current_month():
    date = last_balance_date()
    current_month = date.replace(day=1)
    return current_month

def get_prev_month():
    current = get_current_month()
    prev_month = current - timedelta(days=1)
    prev_month.replace(day=1)
    return prev_month

def get_next_month():
    demo = get_current_month().replace(day=25)
    demo = demo + timedelta(days=10)
    next_month = demo.replace(day=1)
    return next_month