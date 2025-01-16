import datetime
from django.core.exceptions import ValidationError
from .models import Sell, Purchase, StorageReading, Product, Stock, ConsumeStock, Excess, Shortage, InitialStock
from .choices import INITIAL_STOCK, PURCHASE
from Core.functions import prev_day
from Product.views.functions import get_ending_stocks

def stock_in(instance:InitialStock|Purchase):
    date = instance.date
    if isinstance(instance, Purchase):
        stock_in_type   = PURCHASE
    elif isinstance(instance, InitialStock):
        stock_in_type   = INITIAL_STOCK

    Stock.objects.create(
        date            = date,
        product         = instance.product,
        stock_in_type   = stock_in_type,
        initial_stock   = instance if stock_in_type == INITIAL_STOCK else None,
        purchase        = instance if stock_in_type == PURCHASE else None,
        purchase_rate   = instance.purchase_rate
    )

# This doesn't change anything. Just checks stock before saving Sell.
def check_stock(instance:Sell):
    rem_stocks = Stock.objects.filter(
        consumable=True,
        product=instance.product,
        date__lte=instance.date
    )
    # print(rem_stocks,instance)
    status = False
    if rem_stocks:
        ending_quantity = sum(stock.ending for stock in rem_stocks)
        if ending_quantity >= instance.quantity:
            status = True
    if not status: 
        # print(ending_quantity, instance.quantity)
        raise ValidationError(f"{instance.product} এর পর্যাপ্ত পরিমাণ মজুদ নেই! {instance} এর এন্ট্রি সম্ভব হয়নি।")
    return status

def consume_stock(instance:Sell):
    if check_stock(instance):
        product = instance.product
        quantity = instance.quantity
        stocks = Stock.objects.filter(product=product, consumable=True, date__lte=instance.date)
        current_consumed = 0
        while quantity > 0:
            current_stock = stocks.earliest() # FIFO
            # যদি পর্যাপ্ত পরিমাণ স্টক থাকে, বর্তমান স্টক থেকে consume হবে
            if current_stock.ending > quantity:
                current_consumed = quantity
                quantity = 0
            else: # যদি পর্যাপ্ত পরিমাণ স্টক না থাকে, sell quantity থেকে বর্তমান স্টক এর পরিমাণ consume হবে, বাকিটা পরবর্তী স্টক থেকে consume হবে
                quantity -= current_stock.ending
                current_consumed = current_stock.ending
                current_stock.consumable = False
                stocks.exclude(pk=current_stock.pk)
            current_stock.save()

            ConsumeStock.objects.create(
                date    = instance.date,
                stock   = current_stock,
                quantity= current_consumed,
                sell    = instance
            )

def re_consume(from_date, product:Product):
    current_date = from_date
    sells = Sell.objects.filter(date__gte=current_date, product=product)
    if sells:
        to_date = sells.latest().date 
        while current_date <= to_date:
            sells_on_date = sells.filter(date=current_date)
            for sell in sells_on_date:
                consume_stock(sell)
            current_date += datetime.timedelta(days=1)

def delete_consumed(from_date,product:Product):
    consumed = ConsumeStock.objects.filter(
        date__gte=from_date,
        stock__product=product
    )
    for item in consumed: item.delete()

SIGNALS = ['pre','post']
# Common logic to check any change of product and quantity
stock_models = InitialStock|Purchase|Sell|Excess|Shortage
def make_changes(instance:stock_models, todo, signal):
    if instance.pk:
        if signal==SIGNALS[0]: # pre
            prev = instance.__class__.objects.get(pk=instance.pk)
            instance._prev = prev
        elif signal==SIGNALS[1]: # post
            prev = getattr(instance, '_prev', None)
        products = [instance.product]
        # make change only on product or quantity update
        diff_products = prev.product != instance.product
        diff_qnt = prev.quantity != instance.quantity
        if diff_products or diff_qnt:
            if prev.product != instance.product: products.append(prev.product)
            for product in products: todo(instance.date,product)
        if hasattr(instance, 'purchase_rate')  and instance.purchase_rate != prev.purchase_rate:
            # print(instance)
            created = False
            stock = None
            if isinstance(instance, InitialStock):
                stock, created = Stock.objects.get_or_create(
                    initial_stock=instance,
                    defaults= {
                        'date': instance.date,
                        'product': instance.product,
                        'stock_in_type': INITIAL_STOCK,
                        'purchase_rate': instance.purchase_rate,
                    }
                )
            elif isinstance(instance, Purchase):
                stock, created = Stock.objects.get_or_create(
                    purchase=instance,
                    defaults= {
                        'date': instance.date,
                        'product': instance.product,
                        'stock_in_type': INITIAL_STOCK,
                        'purchase_rate': instance.purchase_rate,
                    }
                )
            if stock and not created:
                stock.purchase_rate = instance.purchase_rate
                stock.save()

def handle_storage_reading(instance:StorageReading):
    Excess.objects.filter(date=instance.date,stock__product=instance.product).delete()
    Shortage.objects.filter(date=instance.date,stock__product=instance.product).delete()
    if instance.difference == 0: return None

    consumable_stocks = Stock.objects.filter(
        consumable  = True,
        product     = instance.product,
        date__lte   = instance.date
    )
    total_in_tank = sum(stock.ending for stock in consumable_stocks)
    remaining = abs(instance.difference)
    for stock in consumable_stocks:

        # min_purchase_rate = consumable_stocks.aggregate(Min('purchase_rate__amount'))['purchase_rate__amount__min']
        # targeted_stocks = consumable_stocks.filter(purchase_rate__amount=min_purchase_rate)
        # current_stock = targeted_stocks.earliest()
        if stock != consumable_stocks.last():
            qnt = round(stock.ending/total_in_tank*instance.difference,3)
        else: qnt = remaining
        # Excess --> Stock ++
        if instance.difference > 0:
            Excess.objects.update_or_create(
                date = instance.date,
                stock = stock,
                defaults={
                    'storage_reading':instance,
                    'quantity':qnt
                }
            )
        # Shortage --> Consume ++
        elif instance.difference < 0:
            # if current_stock.ending < instance.difference:
            #     current_stock = targeted_stocks.exclude(pk=current_stock.pk).earliest()
            Shortage.objects.update_or_create(
                date = instance.date,
                stock = stock,
                defaults={
                    'storage_reading':instance,
                    'quantity':abs(qnt)
                }
            )
        remaining -= qnt

def delete_excess_shortage(date,product):
    try:
        excess = Excess.objects.get(date=date,product=product)
        excess.delete()
        shortage = Shortage.objects.get(date=date,product=product)
        shortage.delete()
    except: pass

def set_initial_stock(date):
    products = Product.objects.all()
    prev_date = prev_day(date)
    for product in products:
        ending_stock = get_ending_stocks(prev_date,prev_date,product)
        if ending_stock['save_stock']:
            for row in ending_stock['rate_details']:
                InitialStock.objects.create(
                    date            = date,
                    product         = product,
                    purchase_rate   = row['rate'],
                    quantity        = row['quantity'],
                    price           = row['price']
                )
