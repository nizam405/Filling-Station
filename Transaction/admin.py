from django.contrib import admin
from .models import CashBalance, DailyBalance

# Register your models here.
admin.site.register(CashBalance)
admin.site.register(DailyBalance)