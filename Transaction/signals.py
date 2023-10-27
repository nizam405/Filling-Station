from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import CashBalance
from Ledger.models import CustomerBalance, GroupofCompanyBalance, Profit, Storage
from .functions import last_day_of_month

@receiver(pre_delete, sender=CashBalance)
def delete_balances(sender, instance, **kwargs):
    date = instance.date
    if date == last_day_of_month(date.year, date.month):
        cust_bal = CustomerBalance.objects.filter(month=date.month, year=date.year)
        if cust_bal: cust_bal.delete()
        goc_bal = GroupofCompanyBalance.objects.filter(month=date.month, year=date.year)
        if goc_bal: goc_bal.delete()
        profit = Profit.objects.filter(month=date.month, year=date.year)
        if profit: profit.delete()
        storage = Storage.objects.filter(month=date.month, year=date.year)
        if storage: storage.delete()
