from django.db import models
from django.utils import timezone
from django.urls import reverse

class ProductGroup(models.Model):
    name = models.CharField(max_length=100, verbose_name="মালের নাম")

    def __str__(self):
        return self.name

class Product(models.Model):
    item = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, default=3, verbose_name="আইটেম")
    # name =  models.CharField(max_length=100, verbose_name="মালের নাম")
    TYPE_CHOICES = [
        ('Loose', 'লুস'),
        ('Extra', 'এক্স'),
        ('Pack', 'প্যাক')
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_CHOICES[-1], verbose_name="ধরন")
    brand = models.CharField(max_length=100, blank=True, null=True, verbose_name="ব্র্যান্ড")
    capacity = models.PositiveSmallIntegerField(default=None, null=True, blank=True, verbose_name="পরিমান")
    purchase_rate = models.FloatField(default=None, verbose_name="একক প্রতি ক্রয়মুল্য")
    selling_rate = models.FloatField(default=None, verbose_name="একক প্রতি বিক্রয়মুল্য")

    class Meta:
        ordering = ['item__name']

    def __str__(self):
        output = f"{self.item.name} ({self.get_type_display()})"
        if self.brand: output = f"{self.brand} {self.capacity} লিটার"
        return output
    
    def get_absolute_url(self):
        return reverse("products")

class Purchase(models.Model):
    date = models.DateField(default=timezone.now)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name="মাল")
    quantity = models.FloatField(default=0.0, verbose_name="পরিমাণ")
    rate = models.FloatField(default=0.0, verbose_name="দর")
    amount = models.IntegerField(default=0, verbose_name="মোট")

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"Date: {self.date}, Name: {self.product.item.name}, Amount: {self.amount}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})

class Sell(models.Model):
    date = models.DateField(default=timezone.now)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name="মাল")
    quantity = models.FloatField(default=0.0, verbose_name="পরিমাণ")
    rate = models.FloatField(default=0.0, verbose_name="দর")
    amount = models.IntegerField(default=0, verbose_name="মোট")

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"Date: {self.date}, Name: {self.product.item.name}, Amount: {self.amount}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})