from django.test import TestCase

# Create your tests here.
from Product.models import Product, Purchase, Sell
from Transaction.functions import last_balance_date
import datetime

def purchases():
    date = datetime.date(2024,8,26)
    product = Product.objects.get(name='অকটেন')
    print(date, product)
    purchases = Purchase.objects.filter(date=date, product=product)
    rates = purchases.values('purchase_rate').distinct()
    return rates