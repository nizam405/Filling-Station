from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from .models import Settings
from Transaction.models import DailyBalance

@receiver(post_save, sender=Settings)
def initialize_dailybalance(sender, instance, created, **kwargs):
    if created:
        if instance.start_from_beginning:
            DailyBalance.objects.create(
                date=instance.start_date, 
                cash=0, bank=0, pay_order=0, due_slip=0
                )