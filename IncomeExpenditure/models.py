from django.db import models
from django.urls import reverse
from Transaction.functions import last_balance_date

# Group    
class BaseIncomeExpenditureGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name="নাম")
    serial = models.SmallIntegerField(verbose_name="ক্রম", default=1)

    class Meta:
        ordering = ['serial','name']
        abstract = True

    def __str__(self):
        return self.name
    
    def refactor_serial(self):
        """
        Adjust serial numbers to maintain uniqueness.
        If this serial already exists, shift the conflicting serials.
        """
        conflicting_objects = self.__class__.objects.filter(serial=self.serial).exclude(pk=self.pk)
        while conflicting_objects.exists():
            for obj in conflicting_objects:
                obj.serial += 1
                obj.save()
            # Check again for conflicts in case adjusting one serial created another conflict
            conflicting_objects = self.__class__.objects.filter(serial=self.serial).exclude(pk=self.pk)

    # def save(self, *args, **kwargs):
    #     """
    #     Override the save method to include the refactor_serial logic.
    #     """
    #     super().save(*args, **kwargs)  # Save initially to get a primary key if it's new
    #     self.refactor_serial()
    #     super().save(*args, **kwargs)  # Save again in case the serial was adjusted

class IncomeGroup(BaseIncomeExpenditureGroup):
    def get_absolute_url(self):
        return reverse("create-income-group")
    
class ExpenditureGroup(BaseIncomeExpenditureGroup):
    def get_absolute_url(self):
        return reverse("create-expenditure-group")

# Income/Expenditure
class BaseIncomeExpenditure(models.Model):
    date = models.DateField(default=last_balance_date, verbose_name="তারিখ")
    detail = models.CharField(max_length=255, blank=True, null=True, verbose_name="বিবরণ")
    amount = models.FloatField(null=True, blank=False, verbose_name="টাকা")

    class Meta:
        ordering = ['-date']
        get_latest_by = ['date']

    def __str__(self):
        return f"{self.group.name} - {self.detail} - {self.amount}"
    
class Income(BaseIncomeExpenditure):
    group = models.ForeignKey(IncomeGroup, on_delete=models.SET_NULL, null=True, verbose_name="খাত")
    
    def get_absolute_url(self):
        return reverse('create-income', kwargs={'date':self.date})
    
class Expenditure(BaseIncomeExpenditure):
    group = models.ForeignKey(ExpenditureGroup, on_delete=models.SET_NULL, null=True, verbose_name="খাত")
    
    def get_absolute_url(self):
        return reverse('create-expenditure', kwargs={'date':self.date})