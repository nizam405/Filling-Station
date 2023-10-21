from django.db import models
from django.db.models import Sum, Count
from django.utils import timezone
import datetime
from django.urls import reverse
from Transaction.functions import last_balance_date


# হাওলাদ দাতা
class Lender(models.Model):
    name = models.CharField("নাম", max_length=255)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("lender")

# হাওলাদ গ্রহণ করলে
class BorrowLoan(models.Model):
    date = models.DateField("তারিখ", default=timezone.now, help_text="YYYY-MM-DD")
    lender = models.ForeignKey(to=Lender, on_delete=models.SET_NULL, null=True, verbose_name="হাওলাদ প্রদানকারী")
    amount = models.IntegerField("হাওলাদের পরিমাণ", default=0)
    is_finished = models.BooleanField("পরিশোধিত", default=False)

    def refund_info(self):
        refunds = RefundBorrowedLoan.objects.filter(loan=self.pk)
        if refunds: 
            refund_amount = refunds.aggregate(Sum("amount"))['amount__sum']
        else: 
            refund_amount = 0
        remaining = self.amount - refund_amount
        return (refund_amount, remaining)
    
    @property
    def refund_amount(self):
        refund_amount, remaining = self.refund_info()
        return refund_amount

    @property
    def remaining(self):
        refund_amount, remaining = self.refund_info()
        return remaining
    
    @property
    def can_edit(self):

        if self.date == last_balance_date() + datetime.timedelta(days=1):
            return True
        else: return False
    
    def __str__(self):
        output = f"{self.lender.name} >> হাওলাদ: {self.amount}"
        if self.is_finished: 
            output += " (পরিশোধিত)"
        return output
    
    def get_absolute_url(self):
        return reverse("loan-dashboard")

# গৃহীত হাওলাদের টাকা পরিশোধ করলে
class RefundBorrowedLoan(models.Model):
    date = models.DateField("তারিখ", default=timezone.now, help_text="YYYY-MM-DD")
    loan = models.ForeignKey(to=BorrowLoan, verbose_name="হাওলাদ", on_delete=models.CASCADE, related_name='refunds')
    amount = models.IntegerField("পরিশোধের পরিমাণ", default=0)

    @property
    def remaining(self):
        # Get all refund transactions related to the same loan
        transactions = RefundBorrowedLoan.objects.filter(loan=self.loan)

        # Calculate the total refunded amount
        refund_amount = transactions.aggregate(Sum("amount"))['amount__sum']

        # Calculate the remaining amount
        remaining = self.loan.amount - (refund_amount or 0)
        return remaining
    
    @property
    def can_edit(self):

        if self.date == last_balance_date() + datetime.timedelta(days=1):
            return True
        else: return False

    def __str__(self):
        return f"{self.loan.lender.name} >> হাওলাদ: {self.loan.amount}, পরিশোধ: {self.amount}"
    
    def get_absolute_url(self):
        return reverse("loan-dashboard")

# ---------------------------------------------------------------------------------------------
# হাওলাদ গ্রহীতা
class Borrower(models.Model):
    name = models.CharField("নাম", max_length=255)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("borrower")

# হাওলাড প্রদান করলে
class LendLoan(models.Model):
    date = models.DateField("তারিখ", default=timezone.now, help_text="YYYY-MM-DD")
    borrower = models.ForeignKey(to=Borrower, on_delete=models.SET_NULL, null=True, verbose_name="হাওলাদ গ্রহণকারী")
    amount = models.IntegerField("হাওলাদের পরিমাণ", default=0)
    is_finished = models.BooleanField("পরিশোধিত", default=False)

    def refund_info(self):
        refunds = RefundLendedLoan.objects.filter(loan=self.pk)
        if refunds: 
            refund_amount = refunds.aggregate(Sum("amount"))['amount__sum']
        else: 
            refund_amount = 0
        remaining = self.amount - refund_amount
        return (refund_amount, remaining)
    
    @property
    def refund_amount(self):
        refund_amount, remaining = self.refund_info()
        return refund_amount

    @property
    def remaining(self):
        refund_amount, remaining = self.refund_info()
        return remaining
    
    @property
    def can_edit(self):

        if self.date == last_balance_date() + datetime.timedelta(days=1):
            return True
        else: return False
    
    def __str__(self):
        output = f"{self.borrower.name} >> হাওলাদ: {self.amount}"
        if self.is_finished: 
            output += " (পরিশোধিত)"
        return output
    
    def get_absolute_url(self):
        return reverse("loan-dashboard")

# প্রদত্ত হাওলাদের টাকা ফেরত পেলে
class RefundLendedLoan(models.Model):
    date = models.DateField("তারিখ", default=timezone.now, help_text="YYYY-MM-DD")
    loan = models.ForeignKey(to=LendLoan, verbose_name="হাওলাদ", on_delete=models.CASCADE, related_name='refunds')
    amount = models.IntegerField("ফেরতের পরিমাণ", default=0)

    @property
    def remaining(self):
        transactions = RefundLendedLoan.objects.filter(loan=self.loan)
        if transactions: 
            refund_amount = transactions.aggregate(Sum("amount"))['amount__sum']
        else: 
            refund_amount = 0
        return self.loan.amount - refund_amount
    
    @property
    def can_edit(self):

        if self.date == last_balance_date() + datetime.timedelta(days=1):
            return True
        else: return False
    
    def __str__(self):
        return f"{self.loan.borrower.name} >> হাওলাদ: {self.loan.amount}, পরিশোধ: {self.amount}"
    
    def get_absolute_url(self):
        return reverse("loan-dashboard")