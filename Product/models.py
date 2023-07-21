from typing import Iterable, Optional
from django.db import models
from django.utils import timezone
from django.urls import reverse
import datetime

class Product(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="মালের নাম")
    short_name =  models.CharField(max_length=10, verbose_name="মালের সংক্ষিপ্ত নাম")
    TYPE_CHOICES = [
        ('Loose', 'লুস'),
        ('Pack', 'প্যাক')
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_CHOICES[-1], verbose_name="ধরন")
    need_rescale = models.BooleanField(default=False, verbose_name="মজুদ মাপতে হয়")
    capacity = models.FloatField(default=None, null=True, blank=True, verbose_name="পরিমান")
    # purchase_rate = models.FloatField(default=None, verbose_name="একক প্রতি ক্রয়মুল্য")
    # selling_rate = models.FloatField(default=None, verbose_name="একক প্রতি বিক্রয়মুল্য")
    active = models.BooleanField(default=True, verbose_name='সক্রিয়')

    class Meta:
        ordering = ['type','name','capacity']
    
    def get_purchase_rate(self,date=datetime.date.today()):
        rates = Rate.objects.filter(product=self.pk, date__lte=date).order_by('date')
        if rates:
            rate = rates.last().purchase_rate
        else: rate = 0
        return rate

    def get_selling_rate(self,date=datetime.date.today()):
        rates = Rate.objects.filter(product=self.pk, date__lte=date).order_by('date')
        if rates:
            rate = rates.last().selling_rate
        else: rate = 0
        return rate

    @property
    def purchase_rate(self):
        return self.get_purchase_rate()

    @property
    def selling_rate(self):
        return self.get_selling_rate()

    def __str__(self):
        output = f"{self.name}"
        if self.type == 'Pack': output += f" {self.capacity} লিঃ"
        return output
    
    def get_absolute_url(self):
        return reverse("products")

class Rate(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="মালের নাম")
    date = models.DateField(default=timezone.now, verbose_name="কার্যকরের তারিখ (হইতে)", help_text="YYYY-MM-DD")
    purchase_rate = models.FloatField(default=0, verbose_name="একক প্রতি ক্রয়মুল্য")
    selling_rate = models.FloatField(default=0, verbose_name="একক প্রতি বিক্রয়মুল্য")

    class Meta:
        ordering = ['-date']

    def save(self, *args, **kwargs):
        update = True
        rates = self.__class__.objects.filter(product=self.product)
        if rates:
            last_rate = rates.order_by('date').last()
            last_selling_rate = last_rate.selling_rate
            if not self.selling_rate:
                self.selling_rate = last_selling_rate 
            last_purchase_rate = last_rate.purchase_rate
            if not self.purchase_rate:
                self.purchase_rate = last_purchase_rate 
            if not self.pk and self.selling_rate == last_selling_rate and self.purchase_rate == last_purchase_rate:
                update = False
        # else:
        #     if not self.selling_rate:
        #         self.selling_rate = 0
        #     elif not self.purchase_rate:
        #         self.purchase_rate = 0
        if update:
            return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.date} - Purchase: {self.purchase_rate}, Selling: {self.selling_rate}"
    
    def get_absolute_url(self):
        return reverse("products")

class Purchase(models.Model):
    date = models.DateField(default=timezone.now)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name="মাল", 
        limit_choices_to={'active':True})
    quantity = models.FloatField(default=1, verbose_name="পরিমাণ")
    rate = models.FloatField(default=0, verbose_name="দর")
    amount = models.IntegerField(null=True, blank=False, verbose_name="মোট")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Date: {self.date}, Name: {self.product.name}, Amount: {self.amount}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})

class Sell(models.Model):
    date = models.DateField(default=timezone.now)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name="মাল", 
        limit_choices_to={'active':True})
    quantity = models.FloatField(default=1, verbose_name="পরিমাণ")
    rate = models.FloatField(default=0, verbose_name="দর")
    amount = models.IntegerField(null=True, blank=False, verbose_name="মোট")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Date: {self.date}, Name: {self.product.name}, Amount: {self.amount}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})

class StorageReading(models.Model):
    date = models.DateField(default=timezone.now, verbose_name="তারিখ")
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, limit_choices_to={'need_rescale':True}, verbose_name="মাল")
    tank_deep = models.FloatField(null=True, blank=False, verbose_name="ট্যাংক ডিপ")
    lorry_load = models.FloatField(default=0, verbose_name="লোড")

    @property
    def qnt(self):
        return self.tank_deep+self.lorry_load

    class Meta:
        ordering = ['-date']
        constraints = [models.UniqueConstraint(fields=['date','product'],name='unique_storage_reading')]

    def __str__(self):
        return f"{self.date}: {self.product} - {self.tank_deep}+{self.lorry_load} = {self.qnt}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})