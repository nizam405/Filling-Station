from django.db.models.signals import post_save, post_delete
from django.db.models import Sum
from django.dispatch import receiver

from Customer.choices import INDIVIDUAL, GROUP
from Customer.models import CustomerDue, GroupofCompanyDue, DueSell, DueCollection

# @receiver(post_save, sender=DueSell)
# def handle_duesell(sender, instance:DueSell, created, **kwargs):
#     if not instance.customer.cust_type == INDIVIDUAL:
#         prev_dues = CustomerDue.objects.filter(date__lte=instance.date, customer=instance.customer)
#         prev_due = prev_dues.latest().amount if prev_dues else 0
#         CustomerDue.objects.create()