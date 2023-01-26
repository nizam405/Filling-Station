from django.contrib import admin
from .models import CustomerBalance, GroupofCompanyBalance, Storage

admin.site.register(CustomerBalance)
admin.site.register(GroupofCompanyBalance)
admin.site.register(Storage)
