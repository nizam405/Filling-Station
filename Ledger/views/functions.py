from Product.models import Product, Sell, Purchase, StorageReading
from Ledger.models import Storage
from datetime import date
from django.db.models import Sum

def get_products_info(from_date:date, to_date:date, prev_month:date.month, prev_month_year:date.year):
    sells = Sell.objects.filter(date__gte=from_date,date__lte=to_date)
    purchases = Purchase.objects.filter(date__gte=from_date,date__lte=to_date).order_by('date')
    initial_storages = Storage.objects.filter(month=prev_month, year=prev_month_year)

    products = Product.objects.all()
    product_info = []
    total_profit = 0
    # total_sell_amount = 0
    # total_purchase_amount = 0
    # total_initial_storage_amount = 0
    # total_ending_storage_amount = 0
    for product in products:
        data = {
            'unit': "লিঃ" if product.type == "Loose" else "",
            'ending_storage_reading_amount':0,
            'ending_storage_diff': 0,
            'ending_storage_diff_amount': 0,
            }
        data['product'] = product
        
        # Initial storage - প্রারম্ভিক মজুদ
        storage = initial_storages.filter(product=product)
        initial_qnt = storage.last().quantity if storage else 0
        data['initial_storage'] = initial_qnt
        initial_storage_amount = storage.last().price if storage else 0
        # total_initial_storage_amount += initial_storage_amount
        
        # Purchase - ক্রয়
        purchase = purchases.filter(product=product)
        purchase_qnt = purchase.aggregate(Sum('quantity'))['quantity__sum'] if purchase else 0
        data['purchase_qnt'] = purchase_qnt
        purchase_amount = purchase.aggregate(Sum('amount'))['amount__sum'] if purchase else 0
        data['purchase_amount'] = purchase_amount
        # total_purchase_amount += purchase_amount
        
        rate = product.get_purchase_rate(date=to_date)
        data['purchase_rate'] = rate
        
        # Sell - বিক্রয়
        sell = sells.filter(product=product)
        sell_qnt = sell.aggregate(Sum('quantity'))['quantity__sum'] if sell else 0
        data['sell_qnt'] = sell_qnt
        sell_amount = sell.aggregate(Sum('amount'))['amount__sum'] if sell else 0
        data['sell_amount'] = sell_amount
        # total_sell_amount += sell_amount
        
        # Ending Storage - সমাপনী মজুদ
        ending_qnt = initial_qnt + purchase_qnt - sell_qnt
        data['ending_qnt'] = ending_qnt
        ending_storage_amount = ending_qnt*rate
        data['ending_storage_amount'] = ending_storage_amount
        # total_ending_storage_amount += ending_storage_amount

        if product.need_rescale:
            ending_storage_readings = StorageReading.objects.filter(product=product,date=to_date).order_by('date')
            if ending_storage_readings:
                ending_storage_reading_qnt = ending_storage_readings.last().qnt
                data['ending_storage_reading_qnt'] = ending_storage_reading_qnt
                ending_storage_reading_amount = ending_storage_reading_qnt*rate
                data['ending_storage_reading_amount'] = ending_storage_reading_amount
                # Different
                endding_storage_diff = ending_storage_reading_qnt - ending_qnt
                data['ending_storage_diff'] = endding_storage_diff
                ending_storage_diff_amount = endding_storage_diff*rate
                data['ending_storage_diff_amount'] = ending_storage_diff_amount
        # Profit
        profit = sell_amount + ending_storage_amount - initial_storage_amount - purchase_amount
        data['profit'] = profit
        total_profit += profit
        profit_rate = profit / sell_qnt if sell_qnt > 0 else 0
        data['profit_rate'] = profit_rate
        product_info.append(data)
    # print('sell', total_sell_amount)
    # print('initial_storage', total_initial_storage_amount)
    # print('purchase', total_purchase_amount)
    # print('ending_storage', total_ending_storage_amount)
    return (product_info, total_profit)

            