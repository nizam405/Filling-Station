from django.db import models
from django.utils import timezone
from django.urls import reverse

class Product(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="মালের নাম")
    short_name =  models.CharField(max_length=10, verbose_name="মালের সংক্ষিপ্ত নাম")
    TYPE_CHOICES = [
        ('Loose', 'লুস'),
        ('Pack', 'প্যাক')
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_CHOICES[-1], verbose_name="ধরন")
    need_rescale = models.BooleanField(default=False, verbose_name="মজুদ মাপতে হয়")
    capacity = models.PositiveSmallIntegerField(default=None, null=True, blank=True, verbose_name="পরিমান")
    purchase_rate = models.FloatField(default=None, verbose_name="একক প্রতি ক্রয়মুল্য")
    selling_rate = models.FloatField(default=None, verbose_name="একক প্রতি বিক্রয়মুল্য")

    class Meta:
        ordering = ['type','name','capacity']

    def __str__(self):
        output = f"{self.name}"
        if self.type == 'Pack': output += f" {self.capacity} লিঃ"
        return output
    
    def get_absolute_url(self):
        return reverse("products")

# class Price(models.Model):
#     date = models.DateField(default=timezone.now, verbose_name='তারিখ')
#     product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name="মাল")
#     purchase_rate = models.FloatField(default=None, verbose_name="একক প্রতি ক্রয়মুল্য")
#     selling_rate = models.FloatField(default=None, verbose_name="একক প্রতি বিক্রয়মুল্য")

#     class Meta:
#         ordering = ['-date', 'product']
#         constraints = [models.UniqueConstraint(fields=['date','product'],name='unique_price_date')]

#     def __str__(self):
#         return f"Date: {self.date}, Name: {self.product.name}, Rate: {self.purchase_rate}/{self.selling_rate}"

class Purchase(models.Model):
    date = models.DateField(default=timezone.now)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name="মাল")
    quantity = models.FloatField(default=1, verbose_name="পরিমাণ")
    rate = models.FloatField(default=0, verbose_name="দর")
    amount = models.IntegerField(default=0, verbose_name="মোট")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Date: {self.date}, Name: {self.product.name}, Amount: {self.amount}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})

class Sell(models.Model):
    date = models.DateField(default=timezone.now)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name="মাল")
    quantity = models.FloatField(default=1, verbose_name="পরিমাণ")
    rate = models.FloatField(default=0, verbose_name="দর")
    amount = models.IntegerField(default=0, verbose_name="মোট")

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Date: {self.date}, Name: {self.product.name}, Amount: {self.amount}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})

class StorageReading(models.Model):
    date = models.DateField(default=timezone.now, verbose_name="তারিখ")
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, limit_choices_to={'need_rescale':True}, verbose_name="মাল")
    tank_deep = models.FloatField(default=0, verbose_name="ট্যাংক ডিপ")
    lorry_load = models.FloatField(default=0, verbose_name="লোড")

    class Meta:
        ordering = ['-date']
        constraints = [models.UniqueConstraint(fields=['date','product'],name='unique_storage_reading')]

    def __str__(self):
        return f"{self.date}: {self.product} - {self.tank_deep}+{self.lorry_load}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})