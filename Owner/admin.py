from django.contrib import admin
from .models import Owner, Withdraw, Investment, OwnersEquity, FixedAsset, Profit

admin.site.register(Owner)
admin.site.register(Withdraw)
admin.site.register(Investment)
admin.site.register(OwnersEquity)
admin.site.register(FixedAsset)
admin.site.register(Profit)
