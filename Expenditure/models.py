from django.db import models
from django.urls import reverse
from Transaction.functions import last_balance_date

class ExpenditureGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name="নাম")
    serial = models.SmallIntegerField(verbose_name="ক্রম", default=1)

    class Meta:
        ordering = ['serial','name']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("create-expenditure-group")

class Expenditure(models.Model):
    date = models.DateField(default=last_balance_date, verbose_name="তারিখ")
    group = models.ForeignKey(to=ExpenditureGroup, on_delete=models.SET_NULL, null=True, verbose_name="ব্যয়ের খাত")
    detail = models.CharField(max_length=255, blank=True, null=True, verbose_name="বিবরণ")
    amount = models.FloatField(null=True, blank=False, verbose_name="টাকা")

    class Meta:
        ordering = ['-date']
        get_latest_by = ['date']

    def __str__(self):
        return f"{self.group.name} - {self.detail} - {self.amount}"
    
    def get_absolute_url(self):
        return reverse('create-expenditure', kwargs={'date':self.date})
