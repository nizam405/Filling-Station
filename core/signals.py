from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from .models import Settings
from Transaction.models import CashBalance

@receiver(post_save, sender=Settings)
def initialize_cashbalance(sender, instance:Settings, created, **kwargs):
    if created:
        if instance.start_from_beginning:
            CashBalance.objects.create(date=instance.start_date, amount=0)