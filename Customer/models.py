from django.db import models
from django.utils import timezone
from django.urls import reverse
from Product.models import Product
from .choices import customer_type

class GroupofCompany(models.Model):
    name = models.CharField(max_length=255, verbose_name="নাম")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("groupofcompanies")

class Customer(models.Model):
    name = models.CharField(max_length=255, verbose_name="নাম", unique=True)
    short_name = models.CharField(max_length=25, verbose_name="সংক্ষিপ্ত নাম", null=True, blank=True)
    cust_type = models.CharField(verbose_name="ধরণ", choices=customer_type, default=customer_type[0], max_length=20)
    group = models.ForeignKey(to=GroupofCompany, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="গ্রুপ")
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name="মোবাইল")
    serial = models.SmallIntegerField(default=0, verbose_name="ক্রম")

    class Meta:
        ordering = ['cust_type','group','serial','name']

    def __str__(self):
        txt = self.name
        if self.group:
            txt += f" ({self.group})"
        return txt
    
    def get_absolute_url(self):
        return reverse("customers")

class DueSell(models.Model):
    date = models.DateField(default=timezone.now, verbose_name="তারিখ")
    customer = models.ForeignKey(to=Customer, on_delete=models.SET_NULL, null=True, verbose_name="ক্রেতা")
    product = models.ForeignKey(to=Product, default=1, on_delete=models.SET_NULL, null=True, verbose_name="মাল")
    quantity = models.FloatField(default=1, verbose_name="পরিমাণ")
    rate = models.FloatField(default=0.0, verbose_name="দর")
    amount = models.IntegerField(default=0, verbose_name="মোট")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.customer} - {self.product} - {self.quantity} Ltr. - {self.amount} Tk."
    
    def get_absolute_url(self):
        return reverse('daily-transactions', kwargs={'date':self.date})
    
class DueCollection(models.Model):
    date = models.DateField(default=timezone.now, verbose_name="তারিখ")
    customer = models.ForeignKey(to=Customer, on_delete=models.SET_NULL, null=True, verbose_name="ক্রেতা")
    amount = models.IntegerField(default=0, verbose_name="টাকা")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.customer} - {self.amount}"
    
    def get_absolute_url(self):
        return reverse('daily-transactions', kwargs={'date':self.date})
