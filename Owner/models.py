from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from Transaction.models import CashBalance
from Transaction.functions import last_balance_date, last_balance_date_of_month
from .choices import SHARE_CATEGORY, SPECIFIC_RATE
from Core.functions import prev_day, next_month

class Owner(models.Model):
    name = models.CharField(max_length=255, verbose_name="নাম")
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name="মোবাইল")
    date_created = models.DateField(default=last_balance_date)
    profit_share_category = models.CharField(
        max_length=20, 
        choices=SHARE_CATEGORY, 
        default=SPECIFIC_RATE, 
        verbose_name="লভ্যাংশ প্রাপ্তির ধরণ"
    )
    profit_share = models.FloatField(
        default=1, 
        blank=True,
        verbose_name="প্রাপ্য লভ্যাংশের হার", 
        help_text="সম্পূর্ণ অংশ = 1, ৫০% = 0.5 এভাবে নির্ধারণ করতে হবে।", 
    )
    profit = models.FloatField(
        default=0, blank=True, verbose_name="প্রাপ্য লভ্যাংশ", 
    )

    class Meta:
        ordering = ['name']
        get_latest_by = ['date_created']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("owners")
    
    def validate_share(self):
        if self.profit_share_category == SPECIFIC_RATE:
            if self.profit_share < 0 or self.profit_share > 1:
                raise ValidationError("লভ্যাংশ প্রাপ্তির হার 0 থেকে 1 এর মধ্যে হবে!")
            
            existing_owners = Owner.objects.exclude(pk=self.pk).filter(profit_share_category=SPECIFIC_RATE)
            existing_share = existing_owners.aggregate(total=models.Sum('profit_share'))['total'] or 0

            if existing_share + self.profit_share > 1:
                raise ValidationError("সকল মালিকের মোট অংশ 1 এর বেশি হতে পারবে না!")
    
    def clean(self):
        self.validate_share()
        return super().clean()

class Withdraw(models.Model):
    date = models.DateField(default=last_balance_date, verbose_name='তারিখ')
    owner = models.ForeignKey(to=Owner, on_delete=models.SET_NULL, null=True, verbose_name='মালিক')
    detail = models.CharField(max_length=255, null=True, blank=True, verbose_name='বিবরণ')
    amount = models.IntegerField(null=True, blank=False, verbose_name='পরিমাণ (টাকা)')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.owner} - {self.amount}"

    def get_absolute_url(self):
        return reverse("create-withdraw", kwargs={'date':self.date})

class Investment(models.Model):
    date = models.DateField(default=last_balance_date, verbose_name='তারিখ')
    owner = models.ForeignKey(to=Owner, on_delete=models.SET_NULL, null=True, verbose_name='মালিক')
    detail = models.CharField(max_length=255, null=True, blank=True, verbose_name='বিবরণ')
    amount = models.IntegerField(null=True, blank=False, verbose_name='পরিমাণ (টাকা)')

    class Meta:
        ordering = ['-date']
        get_latest_by = ['date']

    def __str__(self):
        return f"{self.date} - {self.owner} - {self.amount}"

    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})
    
    def save(self, *args, **kwargs):
        cashbalance = CashBalance.objects.filter(date=self.date)
        if cashbalance:
            cashbalance = cashbalance.first()
            cashbalance.amount += self.amount
            cashbalance.save()
        super().save(*args, **kwargs)

class OwnersEquity(models.Model):
    date = models.DateField(default=last_balance_date, verbose_name='তারিখ')
    # Remove month and year
    month = models.IntegerField(default=1, verbose_name="মাস")
    year = models.IntegerField(default=2024, verbose_name="বছর")

    owner = models.ForeignKey(to=Owner, on_delete=models.CASCADE, verbose_name='অংশীদারের নাম')
    profit = models.FloatField(default=0, verbose_name="মুনাফা")
    amount = models.FloatField(null=True, blank=False, verbose_name="পরিমাণ")
    share = models.FloatField(default=0, verbose_name="শতাংশ")

    class Meta:
        # change these
        ordering = ['-date']
        get_latest_by = ['date']
        constraints = [models.UniqueConstraint(fields=['date','owner'], name='unique_ownersequity')]
    
    @property
    def get_profit(self):
        if self.profit: return self.profit
        try:
            profit = Profit.objects.get(date=self.date)
            return profit.amount
        except: return 0
    
    @property
    def withdraw(self):
        qs = Withdraw.objects.filter(
            date__gte = self.date,
            date__lte = last_balance_date_of_month(self.date),
            owner = self.owner
        )
        amount = qs.aggregate(models.Sum('amount'))['amount__sum'] or 0
        return {'queryset': qs, 'amount': amount}
    
    @property
    def investment(self):
        qs = Investment.objects.filter(
            date__gte = self.date,
            date__lte = last_balance_date_of_month(self.date),
            owner = self.owner
        )
        amount = qs.aggregate(models.Sum('amount'))['amount__sum'] or 0
        return {'queryset': qs, 'amount': amount}
    
    @property
    def ending(self):
        try:
            print(next_month(self.date))
            return OwnersEquity.objects.get(
                date = next_month(self.date),
                owner = self.owner
            )
        except: return None

    def __str__(self):
        return f"{self.date} - {self.owner} - {self.amount}"

class FixedAsset(models.Model):
    date = models.DateField(default=last_balance_date, verbose_name='তারিখ')
    name = models.CharField(max_length=255, verbose_name="নাম")
    detail = models.CharField(max_length=255, null=True, blank=True, verbose_name='বিবরণ')
    price = models.IntegerField(null=True, blank=False, verbose_name='মূল্য')

    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.date} - {self.name} - {self.price}/="

    def get_absolute_url(self):
        return reverse("fixed-assets")

class Profit(models.Model):
    date    = models.DateField(default=last_balance_date, verbose_name="তারিখ")
    amount  = models.FloatField(null=True, blank=False, verbose_name="পরিমাণ")

    class Meta:
        ordering        = ['-date']
        get_latest_by   = ['date']
        # constraints = [models.UniqueConstraint(fields=['year','month'], name='unique_profit')]

    def __str__(self):
        return f"{self.date} : {self.amount}"