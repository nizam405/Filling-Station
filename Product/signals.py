from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from .models import Sell, Purchase, Rate, StorageReading, ChangedProduct
from Ledger.models import Storage
from Ledger.functions import save_profit_oe_from, save_storage
from Core.choices import last_day_of_month
from Transaction.functions import get_prev_month
import datetime


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
    # prev_bal_month = get_prev_month() # prev month of last cashbalance date
    # prev_month_last_date = last_day_of_month(prev_bal_month.year,prev_bal_month.month)
    # current_month_last_date = last_day_of_month(instance.date.year,instance.date.month)
    # যদি চলতি মাসের শেষ তারিখ অথবা পূর্বের মাসের লেনদেন হয় তবে ChangedProduct এ রেকর্ড রাখা হবে
    # keep_record = instance.date <= prev_month_last_date or instance.date == current_month_last_date
    # obj = ChangedProduct(date=instance.date, product=instance.product)

    if instance.id is None: # Create Operation
        pass 
        # if keep_record: 
            # Note: নতুন প্রোডাক্ট যুক্ত হলে Cashbalance কম বেশি হতে পারে, তাই Cashbalance আগে Delete করতে হবে
            # ChangedProduct.objects.get_or_create(date=instance.date,product=instance.product)
    else: # Update operation
        prev_instance = instance.__class__.objects.get(id=instance.id)
        product_changed = prev_instance.product != instance.product
        # price_unchanged = prev_instance.price == instance.price
        if product_changed:
            update_rate(prev_instance)
        # if keep_record:
        #     ChangedProduct.objects.get_or_create(date=instance.date,product=instance.product)
        #     if product_changed:
        #         ChangedProduct.objects.get_or_create(date=instance.date,product=prev_instance.product)

# @receiver(post_save, sender=Sell)
# @receiver(post_save, sender=Purchase)
# def adjust_sell(sender, instance, **kwargs):
#     changed = ChangedProduct.objects.all()
#     if changed:
#         current_date = None
#         # Update Storage Ledger of those products
#         for obj in changed:
#             save_storage(obj.date,obj.product)
#             # delete sell
#             current_date = obj.date
#             obj.delete()
#         # Update Profit, OE from concerned date
#         if current_date:
#             save_profit_oe_from(current_date)