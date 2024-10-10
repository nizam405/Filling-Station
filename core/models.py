from django.db import models
from django.contrib.auth.models import User
from .functions import current_year

class Settings(models.Model):
    organization_name = models.CharField(max_length=255, verbose_name='ব্যবসায় প্রতিষ্ঠানের নাম')
    start_from_beginning = models.BooleanField(default=False, verbose_name='ব্যবসায়ের শুরু থেকে হিসাব রাখতে চাই')
    start_date = models.DateField(verbose_name='হিসাব শুরুর তারিখ')
    separate_balances = models.BooleanField(default=False, verbose_name='হাতে নগদ, ব্যাংক জমা, পে-অর্ডার ও ডিউ স্লিপ এর হিসাব পৃথকভাবে রাখা হবে')

    class Meta:
        get_latest_by = ['start_date']
