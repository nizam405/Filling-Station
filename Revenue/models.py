from django.db import models
from django.utils import timezone
from django.urls import reverse

# Create your models here.
class RevenueGroup(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("revenuegroup-list")

class Revenue(models.Model):
    date = models.DateField(default=timezone.now)
    group = models.ForeignKey(to=RevenueGroup, on_delete=models.CASCADE)
    detail = models.CharField(max_length=255)
    amount = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.group.name} - {self.detail} - {self.amount}"
    
    def get_absolute_url(self):
        return reverse('daily-transactions')