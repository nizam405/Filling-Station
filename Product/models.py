from django.db import models
from django.urls import reverse
import datetime
from Transaction.functions import last_balance_date, next_to_last_balance_date

class Product(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True, verbose_name="মালের নাম")
    short_name =  models.CharField(max_length=10, verbose_name="মালের সংক্ষিপ্ত নাম")
    TYPE_CHOICES = [
        ('Loose', 'লুস'),
        ('Pack', 'প্যাক')
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_CHOICES[-1], verbose_name="ধরন")
    need_rescale = models.BooleanField(default=False, verbose_name="মজুদ মাপতে হয়")
    capacity = models.FloatField(default=None, null=True, blank=True, verbose_name="পরিমান")
    active = models.BooleanField(default=True, verbose_name='সক্রিয়')

    class Meta:
        ordering = ['type','name','capacity']
    
    @property
    def last_rate(self):
        rates = Rate.objects.filter(product=self.pk)
        if rates: return rates.latest()
    
    def get_purchase_rate(self,date=datetime.date.today()):
        rates = Rate.objects.filter(product=self.pk, date__lte=date)
        if rates: return rates.latest().purchase_rate 
        else: return 0

    def get_selling_rate(self,date=datetime.date.today()):
        rates = Rate.objects.filter(product=self.pk, date__lte=date)
        if rates: return rates.latest().selling_rate 
        else: return 0

    @property
    def purchase_rate(self):
        return self.get_purchase_rate()
    
    @property
    def purchase_rate_update(self):
        if self.last_rate:
            prev_rate = self.last_rate.prev_rate()
            if prev_rate:
                return self.last_rate.purchase_rate - prev_rate.purchase_rate
            else: return 0
    
    @property
    def monthly_purchase_rate_update(self):
        if self.last_rate:
            prev_month_rate = self.last_rate.prev_month_rate()
            if prev_month_rate:
                return self.last_rate.purchase_rate - prev_month_rate.purchase_rate
            else: return 0

    @property
    def selling_rate(self):
        return self.get_selling_rate()
    
    @property
    def selling_rate_update(self):
        if self.last_rate:
            prev_rate = self.last_rate.prev_rate()
            if prev_rate:
                return self.last_rate.selling_rate - prev_rate.selling_rate
            else: return 0
    
    @property
    def monthly_selling_rate_update(self):
        if self.last_rate:
            prev_month_rate = self.last_rate.prev_month_rate()
            if prev_month_rate:
                return self.last_rate.selling_rate - prev_month_rate.selling_rate
            else: return 0
    
    @property
    def profit_rate(self):
        return self.selling_rate - self.purchase_rate
    
    @property
    def profit_rate_update(self):
        if self.last_rate:
            return self.selling_rate_update - self.purchase_rate_update
    
    @property
    def monthly_profit_rate_update(self):
        if self.last_rate and self.last_rate.prev_rate():
            return self.profit_rate - self.last_rate.prev_rate().profit_rate

    def __str__(self):
        output = f"{self.name}"
        if self.type == 'Pack': output += f" {self.capacity} লিঃ"
        return output
    
    def get_absolute_url(self):
        return reverse("products")

class Rate(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="মালের নাম")
    date = models.DateField(default=next_to_last_balance_date, verbose_name="কার্যকরের তারিখ (হইতে)", help_text="YYYY-MM-DD")
    purchase_rate = models.FloatField(default=0, verbose_name="একক প্রতি ক্রয়মুল্য")
    selling_rate = models.FloatField(default=0, verbose_name="একক প্রতি বিক্রয়মুল্য")

    class Meta:
        ordering = ['-date']
        get_latest_by = "date"

    def prev_rate(self):
        rates = self.__class__.objects.filter(product=self.product, date__lt=self.date)
        if rates:
            return rates.latest()
        else: None

    def prev_month_rate(self, current_month_year=None, current_month=None):
        if current_month_year==None or current_month==None:
            current_month_year = self.date.year
            current_month = self.date.month

        first_day = datetime.date(current_month_year, current_month,1)
        rates = self.__class__.objects.filter(product=self.product, date__lt=first_day)
        if rates:
            return rates.latest()
        else: None
    
    @property
    def prev_month_rate(self):
        return self.prev_month_rate()
    
    @property
    def purchase_rate_update(self):
        if self.prev_rate():
            return self.prev_rate().purchase_rate - self.purchase_rate
        else: return 0
    
    @property
    def selling_rate_update(self):
        if self.prev_rate():
            return self.prev_rate().selling_rate - self.selling_rate
        else: return 0

    @property
    def profit_rate(self):
        return self.selling_rate - self.purchase_rate
    
    @property
    def profit_rate_update(self):
        if self.prev_rate():
            return self.profit_rate - self.prev_rate().profit_rate

    def save(self, *args, **kwargs):
        # Use update_or_create on view, Rate will not have two value on same day
        update = True
        rates = self.__class__.objects.filter(product=self.product)
        if rates: # if the product has prev rate, collect data from it
            last_rate = rates.latest()
            last_selling_rate = last_rate.selling_rate
            if not self.selling_rate:
                self.selling_rate = last_selling_rate 
            last_purchase_rate = last_rate.purchase_rate
            if not self.purchase_rate:
                self.purchase_rate = last_purchase_rate 
            # Don't update if both selling rate and purchase rate have not changed
            if not self.pk and self.selling_rate == last_selling_rate and self.purchase_rate == last_purchase_rate:
                update = False

        if update:
            return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.date} - Purchase: {self.purchase_rate}, Selling: {self.selling_rate}"
    
    def get_absolute_url(self):
        return reverse("products")

class Purchase(models.Model):
    date = models.DateField(default=next_to_last_balance_date)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name="মাল", 
        limit_choices_to={'active':True})
    quantity = models.FloatField(default=1, verbose_name="পরিমাণ")
    rate = models.FloatField(default=0, verbose_name="দর")
    amount = models.IntegerField(null=True, blank=False, verbose_name="মোট")

    class Meta:
        ordering = ['-date']

    @property
    def prev_rate(self):
        rates = Rate.objects.order_by('-date').filter(product=self.product, date__lte=self.date)
        prev_rate = rates.first().purchase_rate if rates else 0
        return prev_rate

    @property
    def rate_status(self):
        status = 'same'
        if self.prev_rate < self.rate: status = 'up'
        elif self.prev_rate > self.rate: status = 'down'
        return status

    def __str__(self):
        return f"Date: {self.date}, Name: {self.product.name}, Amount: {self.amount}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})

class Sell(models.Model):
    date = models.DateField(default=next_to_last_balance_date)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, verbose_name="মাল", 
        limit_choices_to={'active':True})
    quantity = models.FloatField(default=1, verbose_name="পরিমাণ")
    rate = models.FloatField(default=0, verbose_name="দর")
    amount = models.IntegerField(null=True, blank=False, verbose_name="মোট")

    class Meta:
        ordering = ['-date']

    @property
    def prev_rate(self):
        rates = Rate.objects.order_by('-date').filter(product=self.product, date__lte=self.date)
        prev_rate = rates.first().selling_rate if rates else 0
        return prev_rate

    @property
    def rate_status(self):
        status = 'same'
        if self.prev_rate < self.rate: status = 'up'
        elif self.prev_rate > self.rate: status = 'down'
        return status

    def __str__(self):
        return f"Date: {self.date}, Name: {self.product.name}, Amount: {self.amount}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})
    
class ChangedProduct(models.Model):
    date = models.DateField(default=next_to_last_balance_date)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['date']
    def __str__(self):
        return f"Date: {self.date}, Name: {self.product.name}"

class StorageReading(models.Model):
    date = models.DateField(default=last_balance_date, verbose_name="তারিখ")
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE, limit_choices_to={'need_rescale':True}, verbose_name="মাল")
    tank_deep = models.FloatField(null=True, blank=False, verbose_name="ট্যাংক ডিপ")
    lorry_load = models.FloatField(default=0, verbose_name="লোড")

    @property
    def qnt(self):
        return self.tank_deep+self.lorry_load

    class Meta:
        ordering = ['-date']
        constraints = [models.UniqueConstraint(fields=['date','product'],name='unique_storage_reading')]

    def __str__(self):
        return f"{self.date}: {self.product} - {self.tank_deep}+{self.lorry_load} = {self.qnt}"
    
    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})