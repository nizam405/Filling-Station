from django.contrib import admin
from .models import Purchase, Product, Sell, StorageReading, Rate, ChangedProduct
# Register your models here.
admin.site.register(Product)
admin.site.register(Rate)
admin.site.register(Purchase)
admin.site.register(Sell)
admin.site.register(StorageReading)
admin.site.register(ChangedProduct)