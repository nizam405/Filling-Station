from django.contrib import admin
from .models import Customer, GroupofCompany, DueSell, DueCollection

admin.site.register(Customer)
admin.site.register(GroupofCompany)
admin.site.register(DueSell)
admin.site.register(DueCollection)
