from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import RefundBorrowedLoan, RefundLendedLoan

@receiver(post_save, sender=RefundBorrowedLoan)
def update_borrowed_loan(sender, instance, **kwargs):
    loan = instance.loan
    remaining = loan.remaining
    if remaining == 0:
        loan.is_finished = True
    else:
        loan.is_finished = False
    loan.save()
 

@receiver(post_save, sender=RefundLendedLoan)
def finish_lended_loan(sender, instance, **kwargs):
    loan = instance.loan
    remaining = loan.remaining
    if remaining == 0:
        loan.is_finished = True
    else:
        loan.is_finished = False
    loan.save()
