from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.db.models import Sum
from datetime import datetime

from Transaction.models import CashBalance
from Ledger.models import CustomerBalance, GroupofCompanyBalance, Profit, Storage
from Core.functions import last_day_of_month
from Ledger.functions import save_profit_oe, save_storages, save_group_of_company_balance, save_customer_balance

@receiver(pre_delete, sender=CashBalance)
def delete_ledger(sender, instance, **kwargs):
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


@receiver(post_save, sender=CashBalance)
def save_ledger(sender, instance, **kwargs):
    # প্রথমিক ব্যালেন্স সেভ করার সময় খতিয়ান লাগবে না
    if sender.objects.first() != instance:
        date = instance.date
        month = date.month
        year = date.year
        target_date = last_day_of_month(year,month)
        # chek if date is last date of current month
        if target_date == date:
            print("Calculating Ledger")
            start_time = datetime.now()

            save_storages(date)
            save_group_of_company_balance(date)
            save_customer_balance(date)
            
            end_time = datetime.now()
            delta = end_time-start_time
            print("\t(Ledger creation time:",delta.total_seconds(),"sec)")
            save_profit_oe(year,month)
