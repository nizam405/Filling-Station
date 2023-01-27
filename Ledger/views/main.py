from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.db.models import Sum
import datetime
import calendar
from Customer.models import Customer, GroupofCompany, DueSell, DueCollection
from Product.models import Product, Purchase, Sell, StorageReading
from Expenditure.models import ExpenditureGroup
from Revenue.models import RevenueGroup
from Ledger.models import CustomerBalance, GroupofCompanyBalance, Storage
from Ledger.forms import DateFilterForm

class LedgerList(TemplateView):
    template_name = 'Ledger/ledger_list.html'

    def get(self, request, *args, **kwargs):
        today = datetime.date.today()
        current_month = today.month
        current_year = today.year

        if 'month' in self.request.GET and 'year' in self.request.GET:
            self.kwargs['month'] = int(self.request.GET['month'])
            self.kwargs['year'] = int(self.request.GET['year'])
        elif 'month' not in self.kwargs and 'year' not in self.kwargs:
            self.kwargs['month'] = today.month
            self.kwargs['year'] = today.year

        target_date = datetime.date(self.kwargs['year'],self.kwargs['month'],1)
        # Dont let go future
        if target_date > today:
            return redirect('ledger-list', month=current_month, year=current_year)

        prev_month_date = target_date - datetime.timedelta(days=1)
        self.kwargs['prev_month'] = prev_month_date.month
        self.kwargs['prev_month_year'] = prev_month_date.year
        num_days = calendar.monthrange(current_year,current_month)[1]
        self.kwargs['next_date'] = target_date + datetime.timedelta(days=num_days)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = DateFilterForm(self.request.GET or self.kwargs or None)
        context['date_form'] = form
        context['month'] = self.kwargs['month']
        context['year'] = self.kwargs['year']
        context['prev'] = {
            'month': self.kwargs['prev_month'],
            'year': self.kwargs['prev_month_year']
        }
        context['next'] = {
            'month': self.kwargs['next_date'].month,
            'year': self.kwargs['next_date'].year
        }
        # Party
        context.update(self.get_customer_data())
        # Product
        context.update(self.get_product_data())
        # Others
        context['expenditure_group'] = ExpenditureGroup.objects.all()
        context['revenue_group'] = RevenueGroup.objects.all()
        
        return context
    
    def get_customer_data(self):
        context = {}
        customers = []
        total_prev_bal = 0
        total_duesell = 0
        total_collection = 0
        total_bal = 0
        month = self.kwargs['month']
        year = self.kwargs['year']
        prev_month = self.kwargs['prev_month']
        prev_month_year = self.kwargs['prev_month_year']
        # Group of Companies
        group_of_companies = GroupofCompany.objects.all()
        for goc in group_of_companies:
            goc_balances = GroupofCompanyBalance.objects.filter(customer=goc.pk,month=prev_month,year=prev_month_year)
            data = {
                'name': "** " + goc.name,
                'ledger_link': 'groupofcompany-ledger',
                'pk': goc.pk,
                'prev_balance': None,
                'duesell': 0,
                'duecollection': 0,
                'balance': 0,
                }
            if goc_balances:
                last_bal = goc_balances.last()
                # print(last_bal)
                data.update({'prev_balance': last_bal})
                total_prev_bal += last_bal.amount

            duesells = DueSell.objects.filter(date__month=month, date__year=year, customer__group=goc.pk)
            duecollections = DueCollection.objects.filter(date__month=month, date__year=year, customer__group=goc.pk)

            if duesells:
                due_amount = duesells.aggregate(Sum('amount'))['amount__sum']
                total_duesell += due_amount
                data.update({'duesell': due_amount})
            if duecollections:
                collection = duecollections.aggregate(Sum('amount'))['amount__sum']
                total_collection += collection
                data.update({ 'duecollection': collection})
            bal = 0
            bal += data['prev_balance'].amount if data['prev_balance'] else 0
            bal += data['duesell'] - data['duecollection']
            data.update({'balance': bal})
            total_bal += bal
            customers.append(data)
        # Individual Customers
        individual_customers = Customer.objects.filter(cust_type='Individual')
        for customer in individual_customers:
            customer_balances = CustomerBalance.objects.filter(customer=customer.pk,month=prev_month,year=prev_month_year)
            data = {
                'name': customer.name,
                'ledger_link': 'customer-ledger',
                'pk': customer.pk,
                'prev_balance': None,
                'duesell': 0,
                'duecollection': 0,
                'balance': 0,
                }
            if customer_balances:
                last_bal = customer_balances.last()
                data.update({'prev_balance': last_bal})
                total_prev_bal += last_bal.amount

            duesells = DueSell.objects.filter(date__month=month, date__year=year, customer=customer.pk)
            duecollections = DueCollection.objects.filter(date__month=month, date__year=year, customer=customer.pk)
            if duesells:
                due_amount = duesells.aggregate(Sum('amount'))['amount__sum']
                total_duesell += due_amount
                data.update({'duesell': due_amount})
            if duecollections:
                collection = duecollections.aggregate(Sum('amount'))['amount__sum']
                total_collection += collection
                data.update({'duecollection': collection})
            bal = 0
            bal += data['prev_balance'].amount if data['prev_balance'] else 0
            bal += data['duesell'] - data['duecollection']
            data.update({'balance': bal})
            total_bal += bal
            customers.append(data)

        context['customers'] = customers
        context['customers_total'] = {
            'total_prev_bal': total_prev_bal,
            'total_duesell': total_duesell,
            'total_collection': total_collection,
            'total_bal': total_bal,
        }
        return context
    
    def get_product_data(self):
        context = {}
        product_data = []
        total_price = 0
        total_diff_qnt = 0
        total_diff_amount = 0
        month = int(self.kwargs['month'])
        year = int(self.kwargs['year'])
        prev_month = self.kwargs['prev_month']
        prev_month_year = self.kwargs['prev_month_year']
        products = Product.objects.all()
        for product in products:
            pre_storages = Storage.objects.filter(month=prev_month, year=prev_month_year, product=product)
            data = {
                'product': product,
                'unit': "লিঃ" if product.type == "Loose" else "",
                'pre_storage': 0,
                'purchase': 0,
                'sell': 0, # cash + due
                'current_storage': 0, # pre_storage + purchase - sell
                'price': 0, # quantity x purchase rate
                'real_storage': 0,
                'diff_qnt': 0, # current_storage - real_storage
                'diff_amount': 0 # diff_qnt x 
            }
            if pre_storages:
                pre_storage = pre_storages.last()
                data.update({'pre_storage': pre_storage.amount})

            purchases = Purchase.objects.filter(date__month=month, date__year=year, product=product)
            duesells = DueSell.objects.filter(date__month=month, date__year=year, product=product)
            sells = Sell.objects.filter(date__month=month, date__year=year, product=product)
            if purchases:
                purchase_amount = purchases.aggregate(Sum('quantity'))['quantity__sum']
                data.update({'purchase': purchase_amount})
            if duesells:
                sell_amount = duesells.aggregate(Sum('quantity'))['quantity__sum']
                data.update({'sell': sell_amount})
            if sells:
                sell_amount = sells.aggregate(Sum('quantity'))['quantity__sum']
                data.update({'sell': sell_amount})
            data['current_storage'] = data['pre_storage'] + data['purchase'] - data['sell']
            data['price'] = int(data['current_storage']*product.purchase_rate)
            total_price += data['price']
            
            # last_day_month = calendar.monthrange(year,month)[1]
            # last_day = datetime.date(year=year,month=month,day=last_day_month)
            # storage_readings = StorageReading.objects.filter(date=last_day,product=product)
            storage_readings = StorageReading.objects.filter(date__month=month, date__year=year,product=product)
            if storage_readings:
                storage_last = storage_readings.first()
                data['real_storage'] = storage_last.tank_deep + storage_last.lorry_load
                data['diff_qnt'] = data['real_storage'] - data['current_storage']
                total_diff_qnt += data['diff_qnt']
                data['diff_amount'] = int(data['diff_qnt'] * product.purchase_rate)
                total_diff_amount += data['diff_amount']
                
            product_data.append(data)
        context['products'] = product_data
        context['products_total'] = {
            'price': total_price,
            # 'diff-qnt': total_diff_qnt,
            'diff_amount': total_diff_amount
        }
        return context

def saveLedger(request,date):
    month = date.month
    year = date.year
    num_days = calendar.monthrange(year,month)[1]
    target_date = datetime.date(year,month,num_days)
    # chek if date is last date of current month else redirect to daily transactions
    if target_date != date.day:
        return redirect('daily-transactions',date)
    first_date = datetime.date(year,month,1)
    prev_date = first_date - datetime.timedelta(days=1)
    prev_month = prev_date.month
    prev_month_year = prev_date.year

    # Products
    products = Product.objects.all()
    quantity = 0
    for product in products:
        # Diesel and Octen has storage reading
        # they can differ from on paper calculation
        storage_readings = StorageReading.objects.filter(product=product,date=date)
        if product.need_rescale:
            storage = storage_readings.first()
            quantity = storage.tank_deep + storage.lorry_load
        else:
            # Mobil and other pack items need to calculate
            storages = Storage.objects.filter(product=product,month=prev_month,year=prev_month_year)
            # Check if there has previous month storage data
            # Add these to current storage
            # else do not count last storage
            if storages:
                last_storage = storages.last()
                quantity += last_storage.amount
            
            sells = Sell.objects.filter(product=product,date__month=month,date__year=year)
            if sells:
                qnt = sells.aggregate(Sum('quantity'))['quantity__sum']
                quantity -= qnt
            duesells = DueSell.objects.filter(product=product,date__month=month,date__year=year)
            if duesells:
                qnt = duesells.aggregate(Sum('quantity'))['quantity__sum']
                quantity -= qnt
            purchases = Purchase.objects.filter(product=product,date__month=month,date__year=year)
            if purchases:
                qnt = purchases.aggregate(Sum('quantity'))['quantity__sum']
                quantity += qnt
        Storage.objects.update_or_create(
            month=month,year=year,product=product,defaults={'amount': quantity})

    # Customers
    # Group
    group_of_companies = GroupofCompany.objects.all()
    total_amount = 0
    for goc in group_of_companies:
        goc_bal_prev = GroupofCompanyBalance.objects.filter(month=prev_month,year=prev_month_year,customer=goc)
        if goc_bal_prev:
            total_amount += goc_bal_prev.first().amount
        duesells = DueSell.objects.filter(customer__group=goc)
        if duesells:
            amount = duesells.aggregate(Sum('amount'))['amount__sum']
            total_amount += amount
        duecollections = DueCollection.objects.filter(customer__group=goc)
        if duecollections:
            amount = duecollections.aggregate(Sum('amount'))['amount__sum']
            total_amount -= amount
        GroupofCompanyBalance.objects.update_or_create(
            month=month,year=year,customer=goc,defaults={'amount':total_amount})
    # Individual Customer
    total_amount = 0
    customers = Customer.objects.all()
    for customer in customers:
        cust_bal_prev = CustomerBalance.objects.filter(month=prev_month,year=prev_month_year,customer=customer)
        if cust_bal_prev:
            total_amount += cust_bal_prev.first().amount
        duesells = DueSell.objects.filter(customer=customer)
        if duesells:
            amount = duesells.aggregate(Sum('amount'))['amount__sum']
            total_amount += amount
        duecollections = DueCollection.objects.filter(customer=customer)
        if duecollections:
            amount = duecollections.aggregate(Sum('amount'))['amount__sum']
            total_amount -= amount
        CustomerBalance.objects.update_or_create(
            month=month,year=year,customer=customer,defaults={'amount':total_amount})
    return redirect('ledger-list',month=month,year=year)
        