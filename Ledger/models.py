from django.db import models
from django.urls import reverse
from Customer.models import Customer, GroupofCompany
from Product.models import Product, Purchase
from Customer.choices import customer_type
from .choices import MONTHS, YEAR, currentMonth, prevMonth, currentYear
from Core.choices import get_prev_month

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
    price = models.IntegerField(default=0, verbose_name='ক্রয়মুল্য')
    
    class Meta:
        ordering = ['-year','-month','product']
        constraints = [models.UniqueConstraint(fields=['year','month','product'], name='unique_storage')]

    def save(self, *args, **kwargs):
        purchases = Purchase.objects.filter(date__year=self.year, date__month=self.month, product=self.product).order_by('date')
        prev_month_year, prev_month = get_prev_month(self.year,self.month)
        prev_storages = Storage.objects.filter(product=self.product,month=prev_month,year=prev_month_year)
        
        if purchases:
            rate = purchases.last().rate
        elif prev_storages:
            prev_storage = prev_storages.last()
            rate = prev_storage.price / prev_storage.quantity
        else:
            rate = self.product.purchase_rate
        self.price = rate * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.month}, {self.year} - {self.product} - {self.quantity}"
    
    def get_absolute_url(self):
        return reverse('product-topsheet')

class Profit(models.Model):
    month = models.IntegerField(choices=MONTHS, default=prevMonth, verbose_name="মাস")
    year = models.IntegerField(choices=YEAR, default=currentYear, verbose_name="বছর")
    amount = models.IntegerField(null=True, blank=False, verbose_name="পরিমাণ")

    class Meta:
        ordering = ['-year','-month']
        constraints = [models.UniqueConstraint(fields=['year','month'], name='unique_profit')]

    def __str__(self):
        return f"{self.month}, {self.year} - {self.amount}"
    