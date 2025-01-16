from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from Core.functions import account_start_date
from .models import Sell, Purchase, StorageReading, Stock, ConsumeStock, InitialStock
from .functions import stock_in, consume_stock, re_consume, delete_consumed, make_changes, handle_storage_reading, delete_excess_shortage, SIGNALS

# Stock সম্পর্কিত হিসাবগুলি পরিবর্তন করা হলে- 
#   পরিবর্তনের পূর্বে ঐদিন থেকে পরবর্তি সকল consume delete করা হবে
#   এবং পরে পুনরায় consume করা হবে 
# @receiver(pre_save, sender=InitialStock)
# def remove_consumed(sender, instance:InitialStock, **kwargs):
#     if instance.date == account_start_date():
#         make_changes(instance, delete_consumed, SIGNALS[0])

# হিসাব শুরুর তারিখের নতুন প্রারম্ভিক মজুদ Stock এ যুক্ত করা হবে 
# হিসাব শুরুর তারিখের প্রারম্ভিক মজুদ পরিবর্তন করা হলে re_consume হবে
@receiver(post_save, sender=InitialStock)
def add_to_stock(sender, instance:InitialStock, created, **kwargs):
    if instance.date == account_start_date():
        if created: stock_in(instance)
        # else: make_changes(instance, re_consume, SIGNALS[1])

# @receiver(pre_save, sender=Purchase)
# def remove_consumed(sender, instance, **kwargs):
#     make_changes(instance, delete_consumed, SIGNALS[0])

# নতুন ক্রয় Stock এ যুক্ত করা হবে
# পুরাতন ক্রয় পরিবর্তত হলে re_consume হবে
@receiver(post_save, sender=Purchase)
def add_to_stock(sender, instance:Purchase, created, **kwargs):
    stock_in(instance) # remove this
    # if created: stock_in(instance)
    # else: make_changes(instance, re_consume, SIGNALS[1])

# @receiver(pre_save, sender=Sell)
# def handle_sell_presave(sender, instance, **kwargs):
#     make_changes(instance, delete_consumed, SIGNALS[0])

# নতুন বিক্রয় ConsumeStock এ যুক্ত করা হবে
# পুরাতন বিক্রয় পরিবর্তত হলে re_consume হবে
@receiver(post_save, sender=Sell)
def handle_consume_on_sell(sender, instance:Sell, created, **kwargs):
    consume_stock(instance) # remove this
    # if created: consume_stock(instance)
    # else: make_changes(instance, re_consume, SIGNALS[1])

# @receiver(post_delete, sender=Stock)
# def handle_stock_delete(sender, instance:Stock, **kwargs):
#     delete_consumed(instance.date,instance.product)
#     re_consume(instance.date,instance.product)

# @receiver(post_delete, sender=ConsumeStock)
# def reset_consumable(sender, instance:ConsumeStock, **kwargs):
#     stock = instance.stock
#     stock.consumable = True
#     stock.save()

# @receiver(pre_save, sender=StorageReading)
# def remove_consumed(sender, instance, **kwargs):
#     make_changes(instance, delete_excess_shortage, SIGNALS[0])

@receiver(post_save, sender=StorageReading)
def add_storage_reading_to_stock(sender, instance:StorageReading, created, **kwargs):
    handle_storage_reading(instance)
