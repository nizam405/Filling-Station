from django.db.models.signals import pre_save, pre_delete, post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import CashBalance
from Product.functions import handle_storage_reading, set_initial_stock
from Product.models import StorageReading, InitialStock
from Owner.models import Profit
from Owner.functions import generate_net_profit, generate_owners_equity
from Customer.models import CustomerDue, GroupofCompanyDue
from Customer.functions import save_customer_dues
from Core.functions import prev_day, account_start_date, first_date_of_month, prev_month

@receiver(pre_save, sender=CashBalance)
def confirm_storage_reading(sender, instance:CashBalance, **kwargs):
    if instance.date != account_start_date():
        sr = StorageReading.objects.filter(date=prev_day(instance.date))
        if sr.exists(): handle_storage_reading(sr.last())
        else: raise ValidationError("দৈনিক মজুদ মালের হিসাব রাখা হয়নি।")

@receiver(pre_delete, sender=CashBalance)
def delete_ledger(sender, instance:CashBalance, **kwargs):
    # Delete Stock
    stocks = InitialStock.objects.filter(date=instance.date)
    if stocks: stocks.delete()
    if instance.date != account_start_date():
        # Delete Customer Due, GOC Due
        cust_dues = CustomerDue.objects.filter(date=instance.date)
        if cust_dues: cust_dues.delete()
        goc_dues = GroupofCompanyDue.objects.filter(date=instance.date)
        if goc_dues: goc_dues.delete()
        # Delete Profit
        profit = Profit.objects.filter(date=instance.date)
        if profit: profit.delete()

@receiver(post_save, sender=CashBalance)
def save_ledger(sender, instance:CashBalance, created, **kwargs):
    if instance.date != account_start_date():
        set_initial_stock(instance.date)
        if instance.date == first_date_of_month(instance.date):
            from_date = first_date_of_month(prev_month(instance.date))
            to_date = prev_day(instance.date)
            save_customer_dues(from_date,to_date)
            generate_net_profit(from_date,to_date)
            generate_owners_equity(from_date,to_date)