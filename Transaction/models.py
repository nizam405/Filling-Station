from django.db import models
from django.utils import timezone
import datetime
from django.urls import reverse

# Create your models here.
class CashBalance(models.Model):
    date = models.DateField(default=timezone.now, unique=True, verbose_name="তারিখ")
    amount = models.FloatField(null=True, blank=False, verbose_name="পরিমাণ")
    
    class Meta:
        ordering = ['-date']
        get_latest_by = 'date'
    
    @property
    def is_first(self):
        try:
            return self == self.__class__.objects.earliest()
        except self.__class__.DoesNotExist:
            return False
    
    @property
    def is_last(self):
        try:
            return self == self.__class__.objects.latest()
        except self.__class__.DoesNotExist:
            return False

    def __str__(self):
        return f"{self.date} - {self.amount}"
    
    def get_absolute_url(self):
        next_day = self.date + datetime.timedelta(days=1)
        return reverse('daily-transactions', kwargs={'date':next_day})

    # def save(self):
    #     if not self.date:
    #         prev = CashBalance.objects.latest()
    #         self.date = next_day(prev)
    #     return super().save()