from django.db import models
from django.contrib.auth.models import User
from .choices import current_year

class Year(models.Model):
    year = models.IntegerField(default=current_year)

    def __str__(self):
        return self.year

# class Settings(User):
#     business_name = models.CharField(max_length=255)
#     can_change_prev = models.BooleanField(default=False)
#     auto_save_balance = models.BooleanField(default=True)