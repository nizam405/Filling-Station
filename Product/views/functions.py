import datetime
from django.db.models import Sum

from Product.models import Product, Purchase, Sell, ConsumeStock, InitialStock, Excess, Shortage
from Core.functions import accounts_dates_in_month, next_day
from Product.choices import PRODUCT_CATEGORIES

# Product
def get_initial_stocks_queryset(date,product):
    # Prev stock may be any day
    last_init_stocks = InitialStock.objects.filter(date__lte=date,product=product)
    if last_init_stocks: 
        date_last = last_init_stocks.latest().date
        return InitialStock.objects.filter(date=date_last,product=product)
    else: return []
    
def get_initial_stocks(date,product):
    stock = get_initial_stocks_queryset(date,product)
    if stock:
        quantity    = stock.aggregate(Sum('quantity'))['quantity__sum']
        price       = stock.aggregate(Sum('price'))['price__sum']
        # Rate details
        rates = list(set([item.purchase_rate for item in stock]))
        rate_details = []
        for rate in rates:
            stock_of_rate = stock.filter(purchase_rate=rate)
            rate_details.append({
                'rate'      : rate,
                'quantity'  : stock_of_rate.aggregate(Sum('quantity'))['quantity__sum'],
                'price'     : stock_of_rate.aggregate(Sum('price'))['price__sum']
            })
    else: 
        quantity = price = 0
        rate_details = []
    return {
        'quantity'      : quantity,
        'price'         : price,
        'rate_details'  : rate_details,
    }

def get_remaining_stock(from_date,to_date,product,include_excess=False,include_shortage=False):
    save_stock = False
    init_stocks = get_initial_stocks_queryset(date=from_date,product=product)
    purchases = Purchase.objects.filter(date__gte=from_date,date__lte=to_date,product= product)
    consumed_stocks  = ConsumeStock.objects.filter(date__gte=from_date,date__lte=to_date,stock__product=product)
    if include_excess:
        excesses = Excess.objects.filter(date__gte=from_date,date__lte=to_date,stock__product=product)
    if include_shortage:
        shortages = Shortage.objects.filter(date__gte=from_date,date__lte=to_date,stock__product=product)
        # print(shortages)
    # Gather purchase rates
    purchase_rates = set(item.purchase_rate for item in init_stocks if init_stocks) # returns None if not init_stock
    purchase_rates.update(set(item.purchase_rate for item in purchases if purchases))
    purchase_rates.update(set(item.stock.purchase_rate for item in consumed_stocks if consumed_stocks))
    rate_details = []
    total_quantity = total_price = 0
    for rate in purchase_rates:
        if not rate: continue # initial stock may have None
        quantity = price = 0
        init_stocks_of_rate = init_stocks.filter(purchase_rate=rate) if init_stocks else None
        if init_stocks_of_rate:
            qnt = init_stocks_of_rate.aggregate(Sum('quantity'))['quantity__sum']
            quantity    += qnt
            price       += init_stocks_of_rate.aggregate(Sum('price'))['price__sum']
        purchases_of_rate = purchases.filter(purchase_rate=rate) if purchases else None
        if purchases_of_rate:
            qnt = purchases_of_rate.aggregate(Sum('quantity'))['quantity__sum']
            quantity    += qnt
            price       += rate.amount*qnt
        consumes_of_rate = consumed_stocks.filter(stock__purchase_rate=rate) if consumed_stocks else None
        if consumes_of_rate:
            qnt = consumes_of_rate.aggregate(Sum('quantity'))['quantity__sum']
            quantity    -= qnt
            price       -= rate.amount*qnt
        excesses_of_rate = None
        if include_excess:
            excesses_of_rate = excesses.filter(stock__purchase_rate=rate) if excesses else None
            if excesses_of_rate:
                qnt = excesses_of_rate.aggregate(Sum('quantity'))['quantity__sum']
                quantity    += qnt
                price       += rate.amount*qnt
        shortages_of_rate = None
        if include_shortage:
            shortages_of_rate = shortages.filter(stock__purchase_rate=rate) if shortages else None
            if shortages_of_rate:
                qnt = shortages_of_rate.aggregate(Sum('quantity'))['quantity__sum']
                quantity    -= qnt
                price       -= rate.amount*qnt
        rate_details.append({
            'rate'      : rate,
            'quantity'  : quantity,
            'price'     : price
        })
        total_quantity += quantity
        total_price += price
        if quantity > 0 or purchases_of_rate or consumes_of_rate or excesses_of_rate or shortages_of_rate: save_stock = True
    return {
        'quantity'      : total_quantity,
        'price'         : total_price,
        'rate_details'  : rate_details,
        'save_stock'    : save_stock
    }

def get_ending_stocks(from_date,to_date,product:Product):
    next_date = next_day(to_date)
    
    if InitialStock.objects.filter(date=next_date,product=product).exists():
        return get_initial_stocks(next_date,product)
    else: 
        data = get_remaining_stock(from_date,to_date,product,include_excess=True,include_shortage=True)
        return data

def get_total_ending_stock_amount(from_date,to_date):
    products = Product.objects.all()
    price = 0
    for product in products:
        data = get_ending_stocks(from_date,to_date,product)
        price += data['price']
    return price
        
def get_purchases(from_date,to_date,product):
    purchases   = Purchase.objects.filter(date__gte=from_date,date__lte=to_date,product=product)
    quantity    = purchases.aggregate(Sum('quantity'))['quantity__sum'] if purchases else 0
    price       = purchases.aggregate(Sum('price'))['price__sum'] if purchases else 0
    # Rate details
    rates = set(item.purchase_rate for item in purchases)
    rate_details = []
    for rate in rates:
        purchases_of_rate = purchases.filter(purchase_rate=rate)
        rate_details.append({
            'rate'      : rate,
            'quantity'  : purchases_of_rate.aggregate(Sum('quantity'))['quantity__sum'],
            'price'     : purchases_of_rate.aggregate(Sum('price'))['price__sum']
        })
    return {
        'quantity'      : quantity,
        'price'         : price,
        'rate_details'  : rate_details,
    }

def get_sells(from_date,to_date,product):
    sells = Sell.objects.filter(date__gte=from_date,date__lte=to_date,product=product)
    quantity = sells.aggregate(Sum('quantity'))['quantity__sum'] if sells else 0
    price = sells.aggregate(Sum('price'))['price__sum'] if sells else 0

    consume_stocks = ConsumeStock.objects.filter(sell__in=sells)
    profit = consume_stocks.aggregate(Sum('profit'))['profit__sum'] if consume_stocks else 0
    # Rate details
    rates = list(set([item.selling_rate for item in sells]))
    rate_details = []
    for rate in rates:
        sells_of_rate = sells.filter(selling_rate=rate)
        cs = consume_stocks.filter(sell__selling_rate=rate)
        rate_details.append({
            'rate'      : rate,
            'quantity'  : sells_of_rate.aggregate(Sum('quantity'))['quantity__sum'],
            'price'     : sells_of_rate.aggregate(Sum('price'))['price__sum'],
            'profit'    : cs.aggregate(Sum('profit'))['profit__sum'],
        })
    return {
        'quantity'      : quantity,
        'price'         : price,
        'rate_details'  : rate_details,
        'profit'        : profit,
    }

def get_excesses(from_date,to_date,product):
    excesses = Excess.objects.filter(date__gte=from_date,date__lte=to_date,stock__product=product)
    quantity = excesses.aggregate(Sum('quantity'))['quantity__sum'] if excesses else 0
    price = 0
    excess_rates = set(item.stock.purchase_rate for item in excesses)
    rate_details = []
    for rate in excess_rates:
        excess_of_rate = excesses.filter(stock__purchase_rate=rate)
        quantity_of_rate = excess_of_rate.aggregate(Sum('quantity'))['quantity__sum']
        price_of_rate = rate.amount * quantity_of_rate
        price += price_of_rate
        rate_details.append({
            'rate'      : rate,
            'quantity'  : quantity_of_rate,
            'price'     : price_of_rate,
        })
    return {
        'quantity'      : quantity,
        'price'         : price,
        'rate_details'  : rate_details,
    }

def get_shortages(from_date,to_date,product):
    shortages = Shortage.objects.filter(date__gte=from_date,date__lte=to_date,stock__product=product)
    quantity = shortages.aggregate(Sum('quantity'))['quantity__sum'] if shortages else 0
    price = 0
    shortage_rates = set(item.stock.purchase_rate for item in shortages)
    rate_details = []
    for rate in shortage_rates:
        shortage_of_rate = shortages.filter(stock__purchase_rate=rate)
        quantity_of_rate = shortage_of_rate.aggregate(Sum('quantity'))['quantity__sum']
        price_of_rate = rate.amount * quantity_of_rate
        price += price_of_rate
        rate_details.append({
            'rate'      : rate,
            'quantity'  : quantity_of_rate,
            'price'     : price_of_rate,
        })
    return {
        'quantity'      : quantity,
        'price'         : price,
        'rate_details'  : rate_details,
    }

def get_monthly_diff(from_date,to_date,product):
    excess = get_excesses(from_date,to_date,product)
    shortage = get_shortages(from_date,to_date,product)
    quantity = excess['quantity'] - shortage['quantity']
    price = excess['price'] - shortage['price']
    rate = price/quantity if quantity != 0 else 0
    return {
        'quantity'  : quantity,
        'price'     : price,
        'rate'      : rate
    }

def get_sell_profit_details(from_date,to_date,product):
    consumed_stocks = ConsumeStock.objects.filter(
        date__gte       = from_date,
        date__lte       = to_date,
        stock__product  = product
    )
    profit_rates = set(item.profit_rate for item in consumed_stocks)
    rate_details = []
    for rate in profit_rates:
        stocks_of_rate = consumed_stocks.filter(profit_rate=rate)
        rate_details.append({
            'rate': rate,
            'quantity': stocks_of_rate.aggregate(Sum('quantity'))['quantity__sum'] if stocks_of_rate else 0,
            'profit': stocks_of_rate.aggregate(Sum('profit'))['profit__sum'] if stocks_of_rate else 0,
        })
    return {
        'profit': consumed_stocks.aggregate(Sum('profit'))['profit__sum'] if consumed_stocks else 0,
        'rate_details': rate_details
    }

def get_product_details(from_date,to_date,product:Product):
    initial_stocks  = get_initial_stocks(from_date,product)
    purchases       = get_purchases(from_date,to_date,product)
    sells           = get_sells(from_date,to_date,product)

    # Skip if not available
    if initial_stocks['quantity']==0 and purchases['quantity']==0 and sells['quantity']==0: 
        return None
    # Else: include product informations
    data = {
        'product'           : product,
        'initial_stocks'    : initial_stocks,
        'purchases'         : purchases,
        'sells'             : sells,
        'sell_profit'       : get_sell_profit_details(from_date,to_date,product),
        'remaining_stocks'  : get_remaining_stock(from_date,to_date,product),
        'ending_stocks'     : get_ending_stocks(from_date,to_date,product),
    }
    if not product.packaged:
        data['ending_stock_diff'] = get_monthly_diff(from_date,to_date,product)
        data['excesses'] = get_excesses(from_date,to_date,product)
        data['shortages'] = get_shortages(from_date,to_date,product)
    return data

def daily_product_details(from_date,to_date,product:Product):
    dataset = []
    for current_date in accounts_dates_in_month(from_date,to_date):
        data = {'date': current_date}
        product_details = get_product_details(current_date,current_date,product)
        if product_details:
            for key,value in product_details.items():
                data[key] = value
            dataset.append(data)
    total = {
        'purchase'      : { 'quantity': 0, 'price': 0},
        'sell'          : { 'quantity': 0, 'price': 0},
        'sell_profit'   : 0,
        'remaining_stock': {
            'quantity': dataset[-1]['remaining_stocks']['quantity'],
            'price': dataset[-1]['remaining_stocks']['price'],
        },
        'ending_stock': {
            'quantity': dataset[-1]['ending_stocks']['quantity'],
            'price': dataset[-1]['ending_stocks']['price'],
        },
    }
    if not product.packaged:
        total['excess_shortage'] = {
            'quantity': sum(data['ending_stock_diff']['quantity'] for data in dataset),
            'price': sum(data['ending_stock_diff']['price'] for data in dataset),
        }
    for data in dataset:
        total['purchase']['quantity']   += data['purchases']['quantity'] or 0
        total['purchase']['price']      += data['purchases']['price'] or 0
        total['sell']['quantity']       += data['sells']['quantity'] or 0
        total['sell']['price']          += data['sells']['price'] or 0
        total['sell_profit']            += data['sell_profit']['profit'] or 0
    
    return dataset, total

def get_product_category_details(from_date,to_date,category):
    category_dict = dict(PRODUCT_CATEGORIES)

    products = Product.objects.filter(category=category)
    dataset = []
    for product in products:
        data = get_product_details(from_date,to_date,product)
        if data: dataset.append(data) 
    
    total = {
        'initial_stock'     : 0,
        'purchase'          : 0,
        'sell'              : 0,
        'sell_profit'       : 0,
        'remaining_stock'   : 0,
        'excess'            : 0,
        'shortage'          : 0,
        'difference'        : 0,
        'ending_stock'      : 0,
    }
    for data in dataset:
        excess      = data['excesses']['price'] if 'excesses' in data else 0
        shortage    = data['shortages']['price'] if 'shortages' in data else 0
        total['initial_stock']  += data['initial_stocks']['price'] or 0
        total['purchase']       += data['purchases']['price'] or 0
        total['sell']           += data['sells']['price'] or 0
        total['sell_profit']    += data['sell_profit']['profit'] or 0
        total['remaining_stock']+= data['remaining_stocks']['price'] or 0
        total['excess']         += excess
        total['shortage']       += shortage
        total['difference']     += excess-shortage
        total['ending_stock']   += data['ending_stocks']['price'] or 0

    return {
        'category_display': category_dict.get(category),
        'dataset':dataset,
        'total':total
    }

def monthly_product_category_details(from_date,to_date):
    category_details = {}

    for category in PRODUCT_CATEGORIES:
        category_details[category[0]] = get_product_category_details(from_date,to_date,category[0])
        
    total = {
        'initial_stock'     : 0,
        'purchase'          : 0,
        'sell'              : 0,
        'sell_profit'       : 0,
        'remaining_stock'   : 0,
        'excess'            : 0,
        'shortage'          : 0,
        'difference'        : 0,
        'ending_stock'      : 0,
    }
    for data in category_details.values():
        total['initial_stock']  += data['total']['initial_stock']
        total['purchase']       += data['total']['purchase']
        total['sell']           += data['total']['sell']
        total['sell_profit']    += data['total']['sell_profit']
        total['remaining_stock']+= data['total']['remaining_stock']
        total['excess']         += data['total']['excess']
        total['shortage']       += data['total']['shortage']
        total['difference']     += data['total']['difference']
        total['ending_stock']   += data['total']['ending_stock']

    return {'category_details':category_details,'total':total}
    
    
