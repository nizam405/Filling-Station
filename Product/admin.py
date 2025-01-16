from django.contrib import admin
from .models import Purchase, Product, Sell, StorageReading, Rate, PurchaseRate, SellingRate, PurchaseRateVariant, SellingRateVariant, Stock, ConsumeStock, InitialStock,Excess, Shortage
# Register your models here.
class PurchaseRateAdmin(admin.ModelAdmin):
    list_display = ['product','date','variant','amount','active']
    list_filter = ['product','variant','active']
    search_fields = ['product']
    
class SellingRateAdmin(admin.ModelAdmin):
    list_display = ['product','date','variant','amount','active']
    list_filter = ['product','variant','active']
    search_fields = ['product']

admin.site.register(Product)
admin.site.register(Rate)
admin.site.register(PurchaseRateVariant)
admin.site.register(PurchaseRate, PurchaseRateAdmin)
admin.site.register(SellingRateVariant)
admin.site.register(SellingRate, SellingRateAdmin)
admin.site.register(Purchase)
admin.site.register(Sell)
admin.site.register(StorageReading)
admin.site.register(Excess)
admin.site.register(Shortage)
admin.site.register(Stock)
admin.site.register(InitialStock)
admin.site.register(ConsumeStock)