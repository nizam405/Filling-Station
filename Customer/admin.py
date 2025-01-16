from django.contrib import admin
from .models import Customer, GroupofCompany, DueSell, DueCollection, CustomerDue, GroupofCompanyDue

admin.site.register(Customer)
admin.site.register(GroupofCompany)
admin.site.register(DueSell)
admin.site.register(DueCollection)
admin.site.register(CustomerDue)
admin.site.register(GroupofCompanyDue)
