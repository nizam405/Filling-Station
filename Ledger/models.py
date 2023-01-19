from django.db import models
from django.urls import reverse
from Customer.models import Customer, GroupofCompany
from Product.models import ProductGroup
from Customer.choices import customer_type
from .choices import MONTHS, YEAR, currentMonth, currentYear


class CustomerBalance(models.Model):
    month = models.CharField(max_length=20, choices=MONTHS, default=currentMonth, verbose_name="মাস")
    year = models.IntegerField(choices=YEAR, default=currentYear, verbose_name="বছর")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="পার্টি", limit_choices_to={'cust_type': customer_type[0][0]})
    amount = models.IntegerField(default=0, verbose_name="পরিমাণ")

    class Meta:
        ordering = ['-year','month']

    def __str__(self):
        return f"{self.month}, {self.year} - {self.customer}"
    
    def get_absolute_url(self):
        return reverse("customer-ledger", kwargs={"pk": self.pk})
    

class GroupofCompanyBalance(models.Model):
    month = models.CharField(max_length=20, choices=MONTHS, verbose_name="মাস")
    year = models.IntegerField(choices=YEAR, default=currentYear, verbose_name="বছর")
    customer = models.ForeignKey(GroupofCompany, on_delete=models.CASCADE, verbose_name="পার্টি")
    amount = models.IntegerField(default=0, verbose_name="পরিমাণ (টাকা)")

    class Meta:
        ordering = ['-year','month','customer']

    def __str__(self):
        return f"{self.month}, {self.year} - {self.customer}"
    
    def get_absolute_url(self):
        return reverse("groupofcompany-balance")
        # return reverse("groupofcompany-ledger", kwargs={"pk": self.pk})

# class ProductBalance(models.Model):
#     month = models.CharField(max_length=20, choices=MONTHS)
#     year = models.IntegerField(choices=YEAR, default=curentYear)
#     product = models.ForeignKey(ProductGroup, on_delete=models.CASCADE)
#     amount = models.FloatField(default=0)