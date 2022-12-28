from django.db import models
from django.utils import timezone
from datetime import datetime
from django.urls import reverse

# Create your models here.
class Product(models.Model):
    name =  models.CharField(max_length=100, verbose_name="মালের নাম")
    TYPE_CHOICES = [
        ('Loose', 'লুস'),
        ('Pack', 'প্যাক')
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_CHOICES[0], verbose_name="ধরন")
    brand = models.CharField(max_length=100, blank=True, null=True, verbose_name="ব্র্যান্ড")
    capacity = models.PositiveSmallIntegerField(default=None, null=True, blank=True, verbose_name="পরিমান (লিটার)")
    UNIT_CHOICES = [
        ('Liter', 'লিটার'),
        ('Piece', 'পিস '),
    ]
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default=UNIT_CHOICES[0], verbose_name="একক")
    purchase_rate = models.FloatField(default=None, verbose_name="একক প্রতি ক্রয়মুল্য")
    selling_rate = models.FloatField(default=None, verbose_name="একক প্রতি বিক্রয়মুল্য")

    class Meta:
        ordering = ['name']

    def __str__(self):
        output = self.name
        if self.brand: output += f"- {self.brand}"
        return output
    
    def get_absolute_url(self):
        return reverse("product-list")
    

# class SellingRate(models.Model):
#     product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
#     start_date = models.DateField(verbose_name="From Date", default=timezone.now)
#     start_time = models.TimeField(verbose_name="From Time", default=datetime.now)
#     rate = models.FloatField(verbose_name="Rate/Ltr (Tk)")

#     class Meta:
#         ordering = ['start_date','start_time']

#     def __str__(self):
#         return f"{self.product.name} - {self.rate}"
    
#     def get_absolute_url(self):
#         return reverse("selling-rates")

class Purchase(models.Model):
    date = models.DateField(default=timezone.now)
    product = models.ForeignKey(to=Product, on_delete=models.SET_NULL, null=True)
    quantity = models.FloatField(verbose_name="Quantity (Ltr)")
    amount = models.IntegerField(verbose_name="Amount (TK)")
    comment = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.date} - {self.product.name} - {self.amount}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})

class Sell(models.Model):
    date = models.DateField(default=timezone.now)
    product = models.ForeignKey(to=Product, on_delete=models.SET_NULL, null=True)
    quantity = models.FloatField(verbose_name="Quantity (Ltr)")
    amount = models.IntegerField(verbose_name="Amount (TK)")
    comment = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.date} - {self.product.name} - {self.amount}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})