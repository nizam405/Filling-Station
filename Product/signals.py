from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from .models import Sell, Purchase, Rate, StorageReading, Product
from Ledger.models import Storage
from Ledger.functions import save_profit_oe_from
from Core.choices import last_day_of_month, get_prev_month
import datetime

@receiver(post_save, sender=Product)
def create_storage(sender, instance, created, **kwargs):
    if created:
        # প্রারম্ভিক ব্যালেন্সের ক্ষেত্রে (মাসের শেষ দিন) ঐ মাসের তারিখ হবে
        # মাসের শেষ দিন হলে ঐ মাসের তারিখ হবে (মাস শেষ কিন্তু পরের মাসের প্রথম দিন এখনো ব্যালেন্স সেভ করা হয়নি।)
        # এছাড়া বিগত মাস হবে
        year = instance.date_created.year
        month = instance.date_created.month
        if instance.date_created != last_day_of_month(year,month):
            year, month = get_prev_month(year,month)

        Storage.objects.create(month=month, year=year, product=instance, quantity=0, price=0)

@receiver(post_save, sender=StorageReading)
def update_storage(sender,instance:StorageReading, **kwargs):
    year = instance.date.year
    month = instance.date.month
    l_date = last_day_of_month(year,month)
    if l_date == instance.date:
        storages = Storage.objects.filter(year=year,month=month,product=instance.product)
        if storages:
            storage = storages.last()
            storage.quantity = instance.qnt
            storage.save()
            print(f"Ending Storage updated for {year}-{month}")
        current_date = datetime.date(year,month,1)
        save_profit_oe_from(current_date)

def update_rate(instance):
    rates = Rate.objects.filter(product=instance.product,date=instance.date)
    if rates:
        rate = rates.latest()
        delete = False
        prev_rate = rate.prev_rate()
        if isinstance(instance,Sell):
            if prev_rate:
                if rate.purchase_rate == prev_rate.purchase_rate:
                    delete = True
                # if prev rate has selling rate, copy that
                elif prev_rate.selling_rate != 0:
                    rate.selling_rate = prev_rate.selling_rate
                    rate.save()
                    print("Rate updated:",rate.product.name,"Sell:",rate.selling_rate)
            else: # Only purchase rate will be deleted, keep selling rate
                if rate.purchase_rate != 0:
                    rate.selling_rate = 0
                else: delete = True
        elif isinstance(instance,Purchase):
            if prev_rate:
                if rate.selling_rate == prev_rate.selling_rate:
                    delete = True
                # if prev rate has purchase rate, copy that
                elif prev_rate.purchase_rate != 0:
                    rate.purchase_rate = prev_rate.purchase_rate
                    rate.save()
                    print("Rate updated",rate.product.name,"Purchase:",rate.purchase_rate)
            else: # Only purchase rate will be deleted, keep selling rate
                if rate.selling_rate != 0:
                    rate.purchase_rate = 0
                else: delete = True
        if delete: 
            rate.delete()
            print("Rate deleted:",rate.product.name,
                  "Purchase:",rate.purchase_rate,
                  "Selling:",rate.selling_rate)

@receiver(pre_delete, sender=Purchase)
@receiver(pre_delete, sender=Sell)
def on_delete(sender, instance, **kwargs):
    update_rate(instance)

@receiver(pre_save, sender=Sell)
@receiver(pre_save, sender=Purchase)
def on_change(sender, instance, **kwargs):

    if instance.id is not None: # Update operation
        prev_instance = instance.__class__.objects.get(id=instance.id)
        product_changed = prev_instance.product != instance.product
        if product_changed:
            update_rate(prev_instance)
