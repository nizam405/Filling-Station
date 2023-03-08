from django.contrib import admin
from .models import CustomerBalance, GroupofCompanyBalance, Storage, BadDebt, Profit

admin.site.register(CustomerBalance)
admin.site.register(GroupofCompanyBalance)
admin.site.register(Storage)
admin.site.register(BadDebt)
admin.site.register(Profit)
