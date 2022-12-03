from django.db import models
from django.utils import timezone
from datetime import datetime
from django.urls import reverse
from django.conf import settings

# Create your models here.
class Product(models.Model):
    name =  models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        output = self.name
        if self.brand: output += f"- {self.brand}"
        return output
    
    def get_absolute_url(self):
        return reverse("product-list")
    

class SellingRate(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    start_date = models.DateField(verbose_name="From Date", default=timezone.now)
    start_time = models.TimeField(verbose_name="From Time", default=datetime.now)
    rate = models.FloatField(verbose_name="Rate/Ltr (Tk)")

    def __str__(self):
        return f"{self.product.name} - {self.rate}"
    
    def get_absolute_url(self):
        return reverse("selling-rates")

class Purchase(models.Model):
    date = models.DateField(default=timezone.now)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    quantity = models.FloatField(verbose_name="Quantity (Ltr)")
    # rate = models.FloatField(default=0)
    amount = models.FloatField(verbose_name="Amount (TK)")

    def __str__(self):
        return f"{self.date} - {self.product.name} - {self.amount}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions")

class Sell(models.Model):
    date = models.DateField(default=timezone.now)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    quantity = models.FloatField(verbose_name="Quantity (Ltr)")
    # rate = models.OneToOneField(to=SellingRate, on_delete=models.SET_NULL, default=0, null=True)
    amount = models.FloatField(verbose_name="Amount (TK)")

    def __str__(self):
        return f"{self.product.name} - {self.amount} - {self.date}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions")