from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer, GroupofCompany
from Ledger.models import CustomerBalance, GroupofCompanyBalance
from Transaction.models import CashBalance
from Core.functions import get_prev_month

@receiver(post_save, sender=Customer)
def create_customer_balance(sender, instance, created, **kwargs):
    if created:
        cashbalance = CashBalance.objects.order_by('date').last()
        year, month = get_prev_month(cashbalance.date.year,cashbalance.date.month)
        CustomerBalance.objects.create(month=month, year=year, customer=instance, amount=0)


@receiver(post_save, sender=GroupofCompany)
def create_customer_balance(sender, instance, created, **kwargs):
    if created:
        cashbalance = CashBalance.objects.order_by('date').last()
        year, month = get_prev_month(cashbalance.date.year,cashbalance.date.month)
        GroupofCompanyBalance.objects.create(month=month, year=year, customer=instance, amount=0)
        