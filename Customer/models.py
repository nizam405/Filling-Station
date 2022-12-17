from django.db import models
from django.utils import timezone
from django.urls import reverse
from Product.models import Product
from .choices import customer_type

class GroupofCompany(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("groupofcompany-list")

class Customer(models.Model):
    cust_type = models.CharField(verbose_name="Customer Type", choices=customer_type, default=customer_type[0], max_length=20)
    name = models.CharField(max_length=255)
    group = models.ForeignKey(to=GroupofCompany, on_delete=models.SET_NULL, null=True, blank=True)
    default_product = models.ForeignKey(to=Product, on_delete=models.SET_NULL, null=True)
    # default product for something happen in ledger
    mobile = models.CharField(max_length=11, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.cust_type})"
    
    def get_absolute_url(self):
        return reverse("customer-list")
        # return reverse("customer-detail", kwargs={"pk": self.pk})

class DueSell(models.Model):
    date = models.DateField(default=timezone.now)
    customer = models.ForeignKey(to=Customer, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(to=Product, on_delete=models.SET_NULL, null=True)
    quantity = models.FloatField(default=0)
    amount = models.IntegerField(default=0)
    comment = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.date} - {self.customer} - {self.product} - {self.quantity} Ltr. - {self.amount} Tk."
    
    def get_absolute_url(self):
        return reverse('daily-transactions', kwargs={'date':self.date})
    
class DueCollection(models.Model):
    date = models.DateField(default=timezone.now)
    customer = models.ForeignKey(to=Customer, on_delete=models.SET_NULL, null=True)
    amount = models.IntegerField(default=0)
    comment = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.date} - {self.customer} - {self.amount}"
    
    def get_absolute_url(self):
        return reverse('daily-transactions', kwargs={'date':self.date})