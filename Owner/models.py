from django.db import models
from django.utils import timezone
from django.urls import reverse
from Transaction.models import CashBalance
from Ledger.choices import MONTHS, YEAR, currentMonth, currentYear
from Core.choices import get_prev_month
from Ledger.models import Profit

class Owner(models.Model):
    name = models.CharField(max_length=255, verbose_name="নাম")
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name="মোবাইল")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("owners")

class Withdraw(models.Model):
    date = models.DateField(default=timezone.now, verbose_name='তারিখ')
    owner = models.ForeignKey(to=Owner, on_delete=models.SET_NULL, null=True, verbose_name='মালিক')
    detail = models.CharField(max_length=255, null=True, blank=True, verbose_name='বিবরণ')
    amount = models.IntegerField(null=True, blank=False, verbose_name='পরিমাণ (টাকা)')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.owner} - {self.amount}"

    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})

class Investment(models.Model):
    date = models.DateField(default=timezone.now, verbose_name='তারিখ')
    owner = models.ForeignKey(to=Owner, on_delete=models.SET_NULL, null=True, verbose_name='মালিক')
    detail = models.CharField(max_length=255, null=True, blank=True, verbose_name='বিবরণ')
    amount = models.IntegerField(null=True, blank=False, verbose_name='পরিমাণ (টাকা)')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.owner} - {self.amount}"

    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})
    
    def save(self, *args, **kwargs):
        cashbalance = CashBalance.objects.filter(date=self.date)
        if cashbalance:
            cashbalance = cashbalance.first()
            cashbalance.amount += self.amount
            cashbalance.save()
        super().save(*args, **kwargs)

class OwnersEquity(models.Model):
    month = models.IntegerField(choices=MONTHS, default=currentMonth, verbose_name="মাস")
    year = models.IntegerField(choices=YEAR, default=currentYear, verbose_name="বছর")
    owner = models.ForeignKey(to=Owner, on_delete=models.SET_NULL, null=True, verbose_name='মালিক')
    profit = models.IntegerField(default=0, verbose_name="মুনাফা")
    amount = models.IntegerField(null=True, blank=False, verbose_name="পরিমাণ")
    share = models.FloatField(default=0, verbose_name="শতাংশ")

    class Meta:
        ordering = ['-year','-month','owner']
        constraints = [models.UniqueConstraint(fields=['year','month','owner'], name='unique_ownersequity')]

    def __str__(self):
        return f"{self.month}, {self.year} - {self.owner} - {self.amount}"
    
    # def save(self, *args, **kwargs):
    #     if self.share == 0:
    #         profit = Profit.objects.get(month=self.month, year=self.year)
    #         withdraw = Withdraw.objects.filter(date__month=self.month, date__year=self.year, owner=self.owner)
    #         investment = Investment.objects.filter(date__month=self.month, date__year=self.year, owner=self.owner)
    #         pre_month_year, pre_month = get_prev_month(self.year,self.month)
    #         pre_oe = OwnersEquity.objects.filter(month=pre_month, year=pre_month_year, owner=self.owner)
    #     super().save(*args, **kwargs)

class FixedAsset(models.Model):
    date = models.DateField(default=timezone.now, verbose_name='তারিখ')
    name = models.CharField(max_length=255, verbose_name="নাম")
    detail = models.CharField(max_length=255, null=True, blank=True, verbose_name='বিবরণ')
    price = models.IntegerField(null=True, blank=False, verbose_name='মূল্য')

    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date} - {self.name} - {self.price}/="

    def get_absolute_url(self):
        return reverse("fixed-assets")
    