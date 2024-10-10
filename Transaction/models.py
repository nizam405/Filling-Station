from django.db import models
from django.utils import timezone
import datetime
from django.urls import reverse

# Create your models here.
class CashBalance(models.Model):
    date = models.DateField(default=timezone.now, unique=True, verbose_name="তারিখ")
    amount = models.IntegerField(null=True, blank=False, verbose_name="পরিমাণ")
    
    class Meta:
        ordering = ['-date']
        get_latest_by = ['date']
    
    @property
    def is_first(self):
        try:
            return self == self.__class__.objects.earliest()
        except self.__class__.DoesNotExist:
            return False
    
    @property
    def is_last(self):
        try:
            return self == self.__class__.objects.latest()
        except self.__class__.DoesNotExist:
            return False

    def __str__(self):
        return f"{self.date} - {self.amount}"
    
    def get_absolute_url(self):
        next_day = self.date + datetime.timedelta(days=1)
        return reverse('daily-transactions', kwargs={'date':next_day})

class DailyBalance(models.Model):
    date = models.DateField(default=timezone.now, unique=True, verbose_name="তারিখ")
    cash = models.IntegerField(verbose_name="হাতে নগদ", default=0)
    bank = models.IntegerField(verbose_name="ব্যাংক জমা", default=0)
    pay_order = models.IntegerField(verbose_name="পে-অর্ডার", default=0)
    due_slip = models.IntegerField(verbose_name="পে-অর্ডার এর ডিউ স্লিপ", default=0)

    class Meta:
        get_latest_by = ['date']

    @property
    def total(self):
        return self.cash + self.bank + self.pay_order + self.due_slip
    
    @property
    def cashbalance(self):
        try:
            cb = CashBalance.objects.get(date=self.date)
            return cb
        except: return None
    
    @property
    def is_first(self):
        try:
            return self == self.__class__.objects.earliest()
        except self.__class__.DoesNotExist:
            return False
    
    @property
    def is_last(self):
        try:
            return self == self.__class__.objects.latest()
        except self.__class__.DoesNotExist:
            return False
    
    def get_absolute_url(self):
        return reverse("daily-transactions")
    
    
    def __str__(self):
        return f"{self.date} -> balance: {self.total}"