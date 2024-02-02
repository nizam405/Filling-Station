from Product.models import Product, Sell, Purchase, StorageReading
from Ledger.models import Storage, Profit
from Revenue.models import Revenue
from Expenditure.models import Expenditure
from Owner.models import OwnersEquity, Investment, Withdraw, Owner
from Loan.models import BorrowLoan, RefundBorrowedLoan
from Product.models import Product, Purchase, Sell, StorageReading
from Customer.models import Customer, GroupofCompany, DueSell, DueCollection
from Ledger.models import CustomerBalance, GroupofCompanyBalance, Profit, Storage

from datetime import date, datetime
from django.db.models import Sum
from Core.choices import get_prev_month, get_next_month

def save_profit_oe(year,month):
    """
    This method is created to quickly calculate profit and owners equity.
    Used when save multiple Cashbalances, Update transactions in prev month.
    এটা তখনই কাজ করবে, যখন Cashbalance ক্রমান্বয়ে save করা হবে। 
    অর্থাৎ এটা শুধু Cashbalance এর মাসের Profit and Owner equity save হবে।
    """
    prev_y, prev_m = get_prev_month(year,month)

    print("Calculating Net Profit")
    start_time = datetime.now()

    sells = Sell.objects.filter(date__year=year,date__month=month)
    sell_amount = sells.aggregate(Sum('amount'))['amount__sum'] if sells else 0
    purchases = Purchase.objects.filter(date__year=year,date__month=month)
    purchase_amount = purchases.aggregate(Sum('amount'))['amount__sum'] if purchases else 0
    initial_storages = Storage.objects.filter(month=prev_m, year=prev_y)
    initial_storage_amount = initial_storages.aggregate(Sum('price'))['price__sum'] if initial_storages else 0
    ending_storages = Storage.objects.filter(month=month, year=year)
    ending_storage_amount = ending_storages.aggregate(Sum('price'))['price__sum'] if initial_storages else 0
    profit_on_sell = sell_amount + ending_storage_amount - initial_storage_amount - purchase_amount

    revenues = Revenue.objects.filter(date__year=year,date__month=month)
    revenue_amount = revenues.aggregate(Sum('amount'))['amount__sum'] if revenues else 0
    expenditures = Expenditure.objects.filter(date__year=year,date__month=month)
    expenditure_amount = expenditures.aggregate(Sum('amount'))['amount__sum'] if expenditures else 0
    net_profit = profit_on_sell+revenue_amount-expenditure_amount
    saved_profit, created = Profit.objects.update_or_create(
            year=year, month=month, defaults={'amount':net_profit}
        )
    end_time = datetime.now()
    delta = end_time-start_time
    print(f"{saved_profit.get_month_display()}-{saved_profit.year}")
    print(f"\tProfit:{net_profit} (Time:{delta.total_seconds()}sec)")

    print("Calculating Owners' Equity")
    start_time = datetime.now()
    # প্রারম্ভিক মূলধন
    ownersequity = OwnersEquity.objects.filter(year=prev_y,month=prev_m)
    capital_amount = ownersequity.aggregate(Sum('amount'))['amount__sum'] if ownersequity else 0
    # অতিরিক্ত মূলধন
    investments = Investment.objects.filter(date__year=year,date__month=month)
    investment_amount = investments.aggregate(Sum('amount'))['amount__sum'] if investments else 0
    # উত্তোলন
    withdraws = Withdraw.objects.filter(date__year=year,date__month=month)
    withdraw_amount = withdraws.aggregate(Sum('amount'))['amount__sum'] if withdraws else 0
    # পাওনাদার - পাপ্ত হাওলাদ এর বকেয়া
    borrowed_loans = BorrowLoan.objects.filter(date__year__lte=year, date__month__lte=month)
    borrowed_amount = borrowed_loans.aggregate(Sum('amount'))['amount__sum'] if borrowed_loans else 0
    refund_borrowed_loans = RefundBorrowedLoan.objects.filter(date__year__lte=year, date__month__lte=month)
    refund_borrowed_loan_amount = refund_borrowed_loans.aggregate(Sum('amount'))['amount__sum'] if refund_borrowed_loans else 0
    remaining_borrowed_loan = borrowed_amount - refund_borrowed_loan_amount
    owner_profit = net_profit/2
    amount_before_profit = capital_amount + remaining_borrowed_loan + investment_amount - withdraw_amount
    total_oe = amount_before_profit + net_profit
    print("\tTotal owners' equity:",total_oe)

    owners = Owner.objects.all()
    for owner in owners:
        # প্রারম্ভিক মূলধন
        prev_oe = ownersequity.filter(owner=owner)
        prev_oe_amount = prev_oe.last().amount if prev_oe else 0
        
        # অতিরিক্ত মূলধন
        owner_investments = investments.filter(owner=owner)
        owner_investment = owner_investments.aggregate(Sum('amount'))['amount__sum'] if owner_investments else 0
        
        # উত্তোলন
        wds = withdraws.filter(owner=owner)
        wd_amount = wds.aggregate(Sum('amount'))['amount__sum'] if wds else 0
        
        # বর্তমান মালিকানা
        current_oe = prev_oe_amount + owner_investment - wd_amount + owner_profit
        current_share = (current_oe*100)/total_oe

        oe, create = OwnersEquity.objects.update_or_create(
            month=month,year=year,owner=owner,
            defaults={'profit':owner_profit,'amount':current_oe, 'share':current_share})
        print("\t",owner.name, "profit", owner_profit,"Current OE", current_oe, "share", current_share)
    end_time = datetime.now()
    delta = end_time-start_time
    print("\t(Time:",delta.total_seconds(),"sec)")

def save_profit_oe_from(current_date):
    latest_object = Storage.objects.latest()
    end_date = date(latest_object.year,latest_object.month,1)
    # if Storage ledger is calculated, update Storage
    year = current_date.year
    month = current_date.month
    current_date = date(year,month,1)
    while current_date<=end_date:
        # Update Profit & Owners Equity
        save_profit_oe(year,month)
        print(f"Profit and Owners Equity updated for {year}-{month}")
        # Go to next month
        year, month = get_next_month(year,month)
        current_date = date(year,month,1)

def save_storage(date,product):
    month = date.month
    year = date.year
    prev_month_year, prev_month = get_prev_month(year, month)
    quantity = 0
    # Diesel and Octen has storage reading
    # they can differ from on paper calculation
    storage_readings = StorageReading.objects.filter(product=product,date=date)
    if product.need_rescale:
        quantity = storage_readings.last().qnt
    else:
        # Mobil and other pack items need to calculate
        storages = Storage.objects.filter(product=product,month=prev_month,year=prev_month_year)
        # Check if there has previous month storage data
        # Add these to current storage
        # else do not count last storage
        if storages:
            last_storage = storages.last()
            quantity += last_storage.quantity
        
        sells = Sell.objects.filter(product=product,date__month=month,date__year=year)
        if sells:
            qnt = sells.aggregate(Sum('quantity'))['quantity__sum']
            quantity -= qnt
        purchases = Purchase.objects.filter(product=product,date__month=month,date__year=year)
        if purchases:
            qnt = purchases.aggregate(Sum('quantity'))['quantity__sum']
            quantity += qnt
    object,created = Storage.objects.update_or_create(
        month=month,year=year,product=product,defaults={'quantity': quantity})
    print(f"Storage updated - {object}")

def save_storages(date):
    products = Product.objects.all()
    for product in products:
        save_storage(date,product)

def save_group_of_company_balance(date):
    month = date.month
    year = date.year
    prev_month_year, prev_month = get_prev_month(year, month)

    group_of_companies = GroupofCompany.objects.all()
    for goc in group_of_companies:
        goc_bal_prev = GroupofCompanyBalance.objects.filter(month=prev_month,year=prev_month_year,customer=goc).order_by('year','month')
        prev_bal = goc_bal_prev.last().amount if goc_bal_prev else 0

        duesells = DueSell.objects.filter(customer__group=goc, date__month=month, date__year=year)
        due = duesells.aggregate(Sum('amount'))['amount__sum'] if duesells else 0

        duecollections = DueCollection.objects.filter(customer__group=goc, date__month=month, date__year=year)
        collection = duecollections.aggregate(Sum('amount'))['amount__sum'] if duecollections else 0
        
        balance = prev_bal + due - collection
        goc_instance, created = GroupofCompanyBalance.objects.update_or_create(
            month=month,year=year,customer=goc,defaults={'amount':balance})
        if created and goc_bal_prev:
            goc_instance.bad_debt = goc_bal_prev.last().bad_debt
            goc_instance.save()

def save_customer_balance(date):
    month = date.month
    year = date.year
    prev_month_year, prev_month = get_prev_month(year, month)

    customers = Customer.objects.filter(group__isnull=True)
    for customer in customers:
        cust_bal_prev = CustomerBalance.objects.filter(month=prev_month,year=prev_month_year,customer=customer).order_by('year','month')
        prev_bal = cust_bal_prev.last().amount if cust_bal_prev else 0

        duesells = DueSell.objects.filter(customer=customer, date__month=month, date__year=year)
        due = duesells.aggregate(Sum('amount'))['amount__sum'] if duesells else 0

        duecollections = DueCollection.objects.filter(customer=customer, date__month=month, date__year=year)
        collection = duecollections.aggregate(Sum('amount'))['amount__sum'] if duecollections else 0
        
        balance = prev_bal + due - collection
        cust_instance, created = CustomerBalance.objects.update_or_create(
            month=month,year=year,customer=customer,defaults={'amount':balance})
        if created and cust_bal_prev:
            cust_instance.bad_debt = cust_bal_prev.last().bad_debt
            cust_instance.save()

def get_products_info(from_date:date, to_date:date, prev_month:date.month, prev_month_year:date.year):
    """Used in Product Ledger and IncomeStatement"""
    print("Getting product information")
    start_time = datetime.now()

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
        # print(storage.last())
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
        if initial_storage_amount==0 and purchase_amount==0 and sell_amount==0 and ending_storage_amount==0:
            continue
        product_info.append(data)
    end_time = datetime.now()
    delta = end_time-start_time
    print("(Time to get product info:",delta.total_seconds(),"sec)")
    # print('sell', total_sell_amount)
    # print('initial_storage', total_initial_storage_amount)
    # print('purchase', total_purchase_amount)
    # print('ending_storage', total_ending_storage_amount)
    return (product_info, total_profit)

            