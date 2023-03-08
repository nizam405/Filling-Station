from django.contrib import admin
from .models import Owner, Withdraw, Investment, OwnersEquity

admin.site.register(Owner)
admin.site.register(Withdraw)
admin.site.register(Investment)
admin.site.register(OwnersEquity)
