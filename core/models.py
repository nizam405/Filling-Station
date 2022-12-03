from django.db import models
from .choices import current_year

class Year(models.Model):
    year = models.IntegerField(default=current_year)

    def __str__(self):
        return self.year