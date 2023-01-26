from django.db import models
from django.utils import timezone
from django.urls import reverse

class ExpenditureGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name="নাম")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("expenditure-group")

class Expenditure(models.Model):
    date = models.DateField(default=timezone.now)
    group = models.ForeignKey(to=ExpenditureGroup, on_delete=models.SET_NULL, null=True)
    detail = models.CharField(max_length=255, blank=True, null=True)
    amount = models.IntegerField(default=0)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.group.name} - {self.detail} - {self.amount}"
    
    def get_absolute_url(self):
        return reverse('daily-transactions', kwargs={'date':self.date})
