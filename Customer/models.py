from django.db import models
from django.utils import timezone
from django.urls import reverse
from Product.models import Product
from .choices import customer_type

class Customer(models.Model):
    cust_type = models.CharField(verbose_name="Customer Type", choices=customer_type, default=customer_type[0], max_length=20)
    name = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)
    mobile = models.CharField(max_length=11, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    default_product = models.ForeignKey(to=Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.cust_type})"
    
    def get_absolute_url(self):
        return reverse("customer-list")
        # return reverse("customer-detail", kwargs={"pk": self.pk})

class DueSell(models.Model):
    date = models.DateField(default=timezone.now)
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.date} - {self.customer} - {self.product} - {self.quantity} Ltr. - {self.amount} Tk."
    
    def get_absolute_url(self):
        return reverse('daily-transactions')
    
class DueCollection(models.Model):
    date = models.DateField(default=timezone.now)
    customer = models.ForeignKey(to=Customer, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.date} - {self.customer} - {self.amount}"
    
    def get_absolute_url(self):
        return reverse('daily-transactions')