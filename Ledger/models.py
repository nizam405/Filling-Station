from django.db import models
from django.urls import reverse
from Customer.models import Customer, GroupofCompany
from Product.models import Product
from Customer.choices import INDIVIDUAL
from Core.choices import MONTHS
from .choices import YEAR, prevMonth, currentYear
from Product.models import PurchaseRate
from Core.functions import last_day_of_month

# Balance should contain Initial balance.
class CustomerBalance(models.Model):
    month       = models.IntegerField(choices=MONTHS, default=prevMonth, verbose_name="মাস")
    year        = models.IntegerField(choices=YEAR, default=currentYear, verbose_name="বছর")
    customer    = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="পার্টি",
                limit_choices_to={'cust_type': INDIVIDUAL})
    amount      = models.FloatField(null=True, blank=False, verbose_name="পরিমাণ")
    bad_debt    = models.BooleanField(default=False, verbose_name="অনিশ্চিত")

    class Meta:
        ordering = ['-year','-month','customer__serial']

    def __str__(self):
        output = f"{self.month}, {self.year} - {self.customer} - {self.amount}"
        if self.bad_debt: output += " অনিশ্চিত"
        return output
    
    def get_absolute_url(self):
        return reverse("customer-ledger", kwargs={"pk": self.pk})

class GroupofCompanyBalance(models.Model):
    month       = models.IntegerField(choices=MONTHS, default=prevMonth, verbose_name="মাস")
    year        = models.IntegerField(choices=YEAR, default=currentYear, verbose_name="বছর")
    customer    = models.ForeignKey(GroupofCompany, on_delete=models.CASCADE, verbose_name="পার্টি")
    amount      = models.FloatField(null=True, blank=False, verbose_name="পরিমাণ")
    bad_debt    = models.BooleanField(default=False, verbose_name="অনিশ্চিত")

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
    purchase_rate = models.ForeignKey(PurchaseRate, null=True, on_delete=models.SET_NULL)
    rate = models.FloatField(default=0)
    price = models.FloatField(default=0, verbose_name='ক্রয়মুল্য')
    
    class Meta:
        ordering = ['-year','-month','product']
        get_latest_by = ['year','month']
        constraints = [models.UniqueConstraint(fields=['year','month','product','rate'], name='unique_storage')]
    
    @property
    def get_purchase_rate(self):
        date = last_day_of_month(year=self.year,month=self.month)
        rate = self.product.get_purchase_rate(date=date)
        return rate

    def save(self, *args, **kwargs):
        l_day = last_day_of_month(self.year,self.month)
        purchase_rate = PurchaseRate.objects.filter(
            date__lte = l_day, product = self.product,
        ).latest()
        if not self.purchase_rate:
            self.purchase_rate = purchase_rate

        self.rate = self.purchase_rate.amount
        self.price = self.purchase_rate.amount * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        rate = self.get_purchase_rate
        return f"Storage: {self.month}, {self.year} - {self.product} - {self.quantity}x{rate} = {self.price}/="
    
    def get_absolute_url(self):
        return reverse('product-topsheet')

    