from django.db.models.signals import pre_save, pre_delete, post_save, post_delete
from django.dispatch import receiver
from .models import DailyBalance, CashBalance

@receiver(post_save, sender=DailyBalance)
def save_balance(sender, instance, created, **kwargs):
    if created:
        # For first time save
        if sender.objects.count() == 1:
            CashBalance.objects.create(date=instance.date, amount=instance.total)

@receiver(post_delete, sender=DailyBalance)
def delete_balance(sender, instance, **kwargs):
    balance = CashBalance.objects.get(date=instance.date)
    balance.delete()