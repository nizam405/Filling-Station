from django.contrib import admin
from .models import Purchase, ProductGroup, Product
# Register your models here.
admin.site.register(Purchase)
admin.site.register(ProductGroup)
admin.site.register(Product)