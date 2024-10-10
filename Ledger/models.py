from django.db import models
from django.urls import reverse
from Customer.models import Customer, GroupofCompany
from Product.models import Product
from Customer.choices import customer_type
from .choices import MONTHS, YEAR, prevMonth, currentYear
from Core.functions import last_day_of_month

class CustomerBalance(models.Model):
    month = models.IntegerField(choices=MONTHS, default=prevMonth, verbose_name="মাস")
    year = models.IntegerField(choices=YEAR, default=currentYear, verbose_name="বছর")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="পার্টি",
        limit_choices_to={'cust_type': customer_type[0][0]})
    amount = models.IntegerField(null=True, blank=False, verbose_name="পরিমাণ")
    bad_debt = models.BooleanField(default=False, verbose_name="অনিশ্চিত")

    class Meta:
        ordering = ['-year','-month','customer__serial']

    def __str__(self):
        output = f"{self.month}, {self.year} - {self.customer} - {self.amount}"
        if self.bad_debt: output += " অনিশ্চিত"
        return output
    
    def get_absolute_url(self):
        return reverse("customer-ledger", kwargs={"pk": self.pk})

class GroupofCompanyBalance(models.Model):
    month = models.IntegerField(choices=MONTHS, default=prevMonth, verbose_name="মাস")
    year = models.IntegerField(choices=YEAR, default=currentYear, verbose_name="বছর")
    customer = models.ForeignKey(GroupofCompany, on_delete=models.CASCADE, verbose_name="পার্টি")
    amount = models.IntegerField(null=True, blank=False, verbose_name="পরিমাণ")
    bad_debt = models.BooleanField(default=False, verbose_name="অনিশ্চিত")

    class Meta:
        ordering = ['-year','-month','customer']

    def __str__(self):
        output = f"{self.month}, {self.year} - {self.customer} - {self.amount}"
        if self.bad_debt: output += " অনিশ্চিত"
        return output
    
    def get_absolute_url(self):
        return reverse("groupofcompany-balance")

class Storage(models.Model):
    month = models.IntegerField(choices=MONTHS, default=prevMonth, verbose_name="মাস")
    year = models.IntegerField(choices=YEAR, default=currentYear, verbose_name="বছর")
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name="মাল")
    quantity = models.FloatField(default=0, verbose_name="পরিমাণ")
    price = models.FloatField(default=0, verbose_name='ক্রয়মুল্য')
    
    class Meta:
        ordering = ['-year','-month','product']
        get_latest_by = ['year','month']
        constraints = [models.UniqueConstraint(fields=['year','month','product'], name='unique_storage')]
    
    @property
    def get_purchase_rate(self):
        date = last_day_of_month(year=self.year,month=self.month)
        rate = self.product.get_purchase_rate(date=date)
        return rate

    def save(self, *args, **kwargs):
        self.price = self.get_purchase_rate * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        rate = self.get_purchase_rate
        return f"{self.month}, {self.year} - {self.product} - {self.quantity}x{rate} = {self.price}/="
    
    def get_absolute_url(self):
        return reverse('product-topsheet')

class Profit(models.Model):
    month = models.IntegerField(choices=MONTHS, default=prevMonth, verbose_name="মাস")
    year = models.IntegerField(choices=YEAR, default=currentYear, verbose_name="বছর")
    amount = models.FloatField(null=True, blank=False, verbose_name="পরিমাণ")

    class Meta:
        ordering = ['-year','-month']
        get_latest_by = ['-year','-month']
        constraints = [models.UniqueConstraint(fields=['year','month'], name='unique_profit')]

    def __str__(self):
        return f"{self.month}, {self.year} - {self.amount}"
    