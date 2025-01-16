import datetime
from django.db.models import Sum
from .models import CashBalance

def first_balance_date():
    try:
        obj = CashBalance.objects.earliest()
        return obj.date
    except: return datetime.date.today() - datetime.timedelta(days=365*20)

def last_balance_date():
    try:
        obj = CashBalance.objects.latest()
        return obj.date
    except: return datetime.date.today()

def last_balance_date_of_month(date:datetime.date):
    obj = CashBalance.objects.filter(date__year=date.year,date__month=date.month)
    return obj.latest().date if obj else last_balance_date()

def next_to_last_balance_date():
    last = last_balance_date()
    next_date = last + datetime.timedelta(days=1)
    return next_date

def get_current_month():
    date = last_balance_date()
    current_month = date.replace(day=1)
    return current_month

def get_prev_month():
    current = get_current_month()
    prev_month = current - datetime.timedelta(days=1)
    prev_month.replace(day=1)
    return prev_month

def get_next_month():
    demo = get_current_month().replace(day=25)
    demo = demo + datetime.timedelta(days=10)
    next_month = demo.replace(day=1)
    return next_month

def first_ledger_month_date():
    first_bal = first_balance_date()
    demo = first_bal + datetime.timedelta(days=28)
    first_m_date = demo.replace(day=1)
    return first_m_date

def get_cashbalance(date:datetime.date):
    from Product.models import Sell, Purchase
    from IncomeExpenditure.models import Income, Expenditure
    from Customer.models import DueCollection, DueSell
    from Owner.models import Investment, Withdraw
    from Loan.models import BorrowLoan, LendLoan, RefundBorrowedLoan, RefundLendedLoan
    
    try:
        opening_balance = CashBalance.objects.get(date=date)
    except: opening_balance = None
    if opening_balance:
        # Debit
        sell = Sell.objects.filter(date=date).aggregate(Sum('price'))['price__sum'] or 0
        income = Income.objects.filter(date=date).aggregate(Sum('amount'))['amount__sum'] or 0
        due_collection = DueCollection.objects.filter(date=date).aggregate(Sum('amount'))['amount__sum'] or 0
        investment = Investment.objects.filter(date=date).aggregate(Sum('amount'))['amount__sum'] or 0
        borrowed_loan = BorrowLoan.objects.filter(date=date).aggregate(Sum('amount'))['amount__sum'] or 0
        refund_lended_loan = RefundLendedLoan.objects.filter(date=date).aggregate(Sum('amount'))['amount__sum'] or 0
        # Credit
        purchase = Purchase.objects.filter(date=date).aggregate(Sum('price'))['price__sum'] or 0
        expenditure = Expenditure.objects.filter(date=date).aggregate(Sum('amount'))['amount__sum'] or 0
        withdraw = Withdraw.objects.filter(date=date).aggregate(Sum('amount'))['amount__sum'] or 0
        due_sell = DueSell.objects.filter(date=date).aggregate(Sum('price'))['price__sum'] or 0
        lended_loan = LendLoan.objects.filter(date=date).aggregate(Sum('amount'))['amount__sum'] or 0
        refund_borrowed_loan = RefundBorrowedLoan.objects.filter(date=date).aggregate(Sum('amount'))['amount__sum'] or 0
        # Balance
        closing_balance = opening_balance.amount
        closing_balance += sell + income + due_collection + investment + borrowed_loan + refund_lended_loan
        closing_balance -= purchase + expenditure + withdraw + due_sell + lended_loan + refund_borrowed_loan
        return closing_balance

def save_cashbalance(date:datetime.date):
    closing_balance = get_cashbalance(date)
    # print(closing_balance)
    CashBalance.objects.update_or_create(
        date=next_to_last_balance_date(), 
        defaults={'amount':closing_balance}
    )

