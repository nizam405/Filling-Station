from django.db import models
from django.utils import timezone
from django.urls import reverse

class Owner(models.Model):
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=11, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    # ownership = models.FloatField()
    address = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("owner-detail", kwargs={"pk": self.pk})

class Withdraw(models.Model):
    date = models.DateField(default=timezone.now)
    owner = models.ForeignKey(to=Owner, on_delete=models.SET_NULL, null=True)
    amount = models.IntegerField(default=0)
    comment = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.date} - {self.owner} - {self.amount}"

    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})

class Investment(models.Model):
    date = models.DateField(default=timezone.now)
    owner = models.ForeignKey(to=Owner, on_delete=models.SET_NULL, null=True)
    amount = models.IntegerField(default=0)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.date} - {self.owner} - {self.amount}"

    def get_absolute_url(self):
        return reverse("daily-transactions", kwargs={'date':self.date})