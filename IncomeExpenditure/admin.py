from django.contrib import admin
from .models import ExpenditureGroup, Expenditure, IncomeGroup, Income

admin.site.register(ExpenditureGroup)
admin.site.register(Expenditure)
admin.site.register(IncomeGroup)
admin.site.register(Income)
