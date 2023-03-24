from django.shortcuts import redirect, render
from django.forms import modelformset_factory
from django.views.generic import TemplateView
from django.db.models import Sum, Count
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from Customer.models import Customer, GroupofCompany, DueSell, DueCollection
from Product.models import Product
from Ledger.models import CustomerBalance, GroupofCompanyBalance
from Ledger.forms import (CustomerLedgerFilterForm, GroupofCompanyLedgerFilterForm, DateFilterForm, 
    CustomerBalanceForm, GroupofCompanyBalanceForm)
from Transaction.models import CashBalance
from Core.choices import last_day_of_month

class CustomerTopSheet(LoginRequiredMixin,TemplateView):
    template_name = 'Ledger/customer_topsheet.html'

    def get(self, request, *args, **kwargs):
        if not CashBalance.objects.exists():
            return redirect('create-cashbalance')
        
        first_bal_date = CashBalance.objects.order_by('date').first().date
        last_bal_date = CashBalance.objects.order_by('date').last().date

        first_date = datetime.date(first_bal_date.year,first_bal_date.month,1)
        first_date = first_date + datetime.timedelta(days=31)

        if 'month' in self.request.GET and 'year' in self.request.GET:
            self.kwargs['month'] = int(self.request.GET['month'])
            self.kwargs['year'] = int(self.request.GET['year'])
        elif 'month' not in self.kwargs and 'year' not in self.kwargs:
            self.kwargs['month'] = last_bal_date.month
            self.kwargs['year'] = last_bal_date.year
        month = self.kwargs['month']
        year = self.kwargs['year']
        
        target_date = datetime.date(year,month,1)
        # Dont let go future
        if target_date > last_bal_date:
            return redirect('customer-topsheet', month=last_bal_date.month, year=last_bal_date.year)
        elif target_date <= first_bal_date:
            return redirect('customer-topsheet', month=first_date.month, year=first_date.year)

        prev_month_date = target_date - datetime.timedelta(days=1)
        self.kwargs['prev_month'] = prev_month_date.month
        self.kwargs['prev_month_year'] = prev_month_date.year
        # here num_days+7 to make sure it goes to next month
        self.kwargs['next_date'] = target_date + datetime.timedelta(days=31)

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
        
        customers = []
        total_prev_bal = 0
        total_duesell = 0
        total_collection = 0
        total_bal = 0
        month = self.kwargs['month']
        year = self.kwargs['year']
        prev_month = self.kwargs['prev_month']
        prev_month_year = self.kwargs['prev_month_year']
        from_date = datetime.date(year,month,1)
        to_date = CashBalance.objects.filter(date__month=month,date__year=year).order_by('date').last().date
        last_day = last_day_of_month(year,month)
        context['status'] = last_day == to_date
        context['to_date'] = to_date
        # Group of Companies
        group_of_companies = GroupofCompany.objects.all()
        for goc in group_of_companies:
            goc_balances = GroupofCompanyBalance.objects.filter(
                customer=goc.pk, month=prev_month, year=prev_month_year)
            data = {
                'name': "** " + goc.name,
                'ledger_link': 'groupofcompany-ledger',
                'link_css': "text-dark",
                'pk': goc.pk,
                'prev_balance': None,
                'duesell': 0,
                'duecollection': 0,
                'balance': 0,
                'baddebt': False,
                }
            if goc_balances:
                last_bal = goc_balances.last()
                data.update({'prev_balance': last_bal})
                total_prev_bal += last_bal.amount
                if last_bal.bad_debt: 
                    data['baddebt'] = True
                    data['link_css'] = "text-secondary"

            duesells = DueSell.objects.filter(date__gte=from_date, date__lte=to_date, customer__group=goc.pk)
            duecollections = DueCollection.objects.filter(date__gte=from_date, date__lte=to_date, customer__group=goc.pk)
            if duesells or duecollections: data['baddebt'] = False

            due_amount = 0
            if duesells:
                due_amount = duesells.aggregate(Sum('amount'))['amount__sum']
                total_duesell += due_amount
                data.update({'duesell': due_amount})
            
            collection = 0
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
            customer_balances = CustomerBalance.objects.filter(
                customer=customer.pk,month=prev_month,year=prev_month_year)
            data = {
                'name': customer.name,
                'ledger_link': 'customer-ledger',
                'link_css': "text-dark",
                'pk': customer.pk,
                'prev_balance': None,
                'duesell': 0,
                'duecollection': 0,
                'balance': 0,
                'baddebt': False,
                }
            if customer_balances:
                last_bal = customer_balances.last()
                data.update({'prev_balance': last_bal})
                total_prev_bal += last_bal.amount
                if last_bal.bad_debt: 
                    data['baddebt'] = True
                    data['link_css'] = "text-secondary"

            duesells = DueSell.objects.filter(date__gte=from_date, date__lte=to_date, customer=customer.pk)
            duecollections = DueCollection.objects.filter(date__gte=from_date, date__lte=to_date, customer=customer.pk)
            if duesells or duecollections: data['baddebt'] = False
            
            due_amount = 0
            if duesells:
                due_amount = duesells.aggregate(Sum('amount'))['amount__sum']
                total_duesell += due_amount
                data.update({'duesell': due_amount})
            collection = 0
            if duecollections:
                collection = duecollections.aggregate(Sum('amount'))['amount__sum']
                total_collection += collection
                data.update({'duecollection': collection})
            
            bal = 0
            last_bal = data['prev_balance'].amount if data['prev_balance'] else 0
            bal += last_bal
            # কোনো কার্যকলাপ না থাকলে টপশিটে আসবে না
            if last_bal == 0 and due_amount == 0 and collection == 0:
                continue
            
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

class CustomerLedger(LoginRequiredMixin,TemplateView):
    template_name = 'Ledger/customer.html'

    def get(self, request, *args, **kwargs):
        if not CashBalance.objects.exists():
            return redirect('create-cashbalance')
        
        today = datetime.date.today()
        # Customer
        if 'customer' in self.request.GET:
            self.kwargs['customer'] = self.request.GET.get('customer')
        elif 'customer' not in self.kwargs:
            self.kwargs['customer'] = Customer.objects.filter(cust_type='Individual').first().pk
        # Month and year
        if 'month' in self.request.GET and 'year' in self.request.GET:
            self.kwargs['month'] = int(self.request.GET.get('month'))
            self.kwargs['year'] = int(self.request.GET.get('year'))
        elif 'month' not in self.kwargs and 'year' not in self.kwargs:
            self.kwargs['month'] = today.month
            self.kwargs['year'] = today.year

        customer = self.kwargs['customer']
        month = self.kwargs['month']
        year = self.kwargs['year']
        target_date = datetime.date(year,month,1)
        self.kwargs['target_date'] = target_date

        balances = CustomerBalance.objects.filter(customer=customer).order_by('year','month')
        if balances.count() == 0:
            context = self.get_context_data()
            return super(TemplateView, self).render_to_response(context)

        last_balance = balances.last()
        first_balance = balances.first()

        first_bal_date = datetime.date(int(first_balance.year), int(first_balance.month),1)
        last_bal_date = datetime.date(int(last_balance.year), int(last_balance.month),1)
        next_to_first = first_bal_date + datetime.timedelta(days=31)
        next_to_last = last_bal_date + datetime.timedelta(days=31)

        if target_date > next_to_last:
            return redirect('customer-ledger', 
                customer = self.kwargs['customer'], 
                month = next_to_last.month, 
                year = next_to_last.year)
        elif target_date < next_to_first:
            return redirect('customer-ledger', 
                customer = self.kwargs['customer'], 
                month = next_to_first.month, 
                year = next_to_first.year)

        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        customer = self.kwargs['customer']
        month = self.kwargs['month']
        year = self.kwargs['year']
        target_date = self.kwargs['target_date']
        prev_date = target_date - datetime.timedelta(days=1)
        next_date = target_date + datetime.timedelta(days=31)
        context['prev'] = prev_date
        context['next'] = next_date
        from_date = datetime.date(year,month,1)
        to_date = CashBalance.objects.filter(date__month=month,date__year=year).order_by('date').last().date

        context['filter_form'] = CustomerLedgerFilterForm(self.kwargs or None)
        context['customer'] = Customer.objects.get(pk=customer)
        balances = CustomerBalance.objects.filter(customer=customer, year=prev_date.year, month=prev_date.month)

        context['balance_bf'] = balances.last().amount if balances else 0
        context['balance_bf_date'] = datetime.date(year,month,1)
        context['has_balance'] = True
        # Data
        duesells = DueSell.objects.filter(customer=customer, date__gte=from_date, date__lte=to_date)
        duecollections = DueCollection.objects.filter(customer=customer, date__gte=from_date, date__lte=to_date)
        
        data = []
        dates = [obj['date'] for obj in duesells.values("date").distinct()]
        for obj in duecollections.values("date").distinct():
            if obj['date'] not in dates:
                dates.append(obj['date'])

        # total_diesel = 0
        dates = sorted(dates)
        for date in dates:
            sells = duesells.filter(date=date)
            collection = duecollections.filter(date=date)
            data_today = {
                'date': date,
                'sells': sells,
                'amount': sells.aggregate(Sum("amount"))["amount__sum"] if sells.count() > 0 else False,
                'collection': collection.aggregate(Sum("amount"))["amount__sum"] if collection.count() > 0 else False
            }                
            data.append(data_today)
        
        balance = context['balance_bf']
        # data = sorted(data, key=lambda x:x['date'])
        for obj in data:
            if 'amount' in obj:
                balance += obj['amount']
            if 'collection' in obj:
                balance -= obj['collection']
            obj.update({'balance': balance})
        context['qs'] = data

        products = Product.objects.all()
        summary = []
        for product in products:
            prod = duesells.filter(product=product)
            if prod.count() > 0:
                qnt = prod.aggregate(Sum('quantity'))['quantity__sum']
                amount = prod.aggregate(Sum('amount'))['amount__sum']
                summary.append({
                    'product': product,
                    'quantity': qnt,
                    'amount': amount
                })
        context['summary'] = summary
        total_sell = duesells.aggregate(Sum("amount"))['amount__sum'] if duesells else 0
        total_collection = duecollections.aggregate(Sum("amount"))['amount__sum'] if duecollections else 0
        context['total_sell'] = total_sell
        context['total_collection'] = total_collection
        context['balance_cf'] = context['balance_bf'] + total_sell - total_collection
        return context

class GroupofCompanyLedger(LoginRequiredMixin,TemplateView):
    template_name = 'Ledger/groupofcompany.html'

    def get(self, request, *args, **kwargs):
        if not CashBalance.objects.exists():
            return redirect('create-cashbalance')
        
        today = datetime.date.today()
        # customer
        if 'customer' in self.request.GET:
            self.kwargs['customer'] = self.request.GET.get('customer')
        elif 'customer' not in self.kwargs:
            self.kwargs['customer'] = GroupofCompany.objects.first().pk
        # Month and year
        if 'month' in self.request.GET and 'year' in self.request.GET:
            self.kwargs['month'] = int(self.request.GET.get('month'))
            self.kwargs['year'] = int(self.request.GET.get('year'))
        elif 'month' not in self.kwargs and 'year' not in self.kwargs:
            self.kwargs['month'] = today.month
            self.kwargs['year'] = today.year

        customer = self.kwargs['customer']
        
        month = self.kwargs['month']
        year = self.kwargs['year']

        balances = GroupofCompanyBalance.objects.filter(customer=customer).order_by('year','month')
        if balances.count() == 0:
            context = self.get_context_data()
            return super(TemplateView, self).render_to_response(context)

        last_balance = balances.last()
        first_balance = balances.first()

        target_date = datetime.date(year,month,1)
        self.kwargs['target_date'] = target_date
        first_bal_date = datetime.date(int(first_balance.year), int(first_balance.month),1)
        last_bal_date = datetime.date(int(last_balance.year), int(last_balance.month),1)
        next_to_first = first_bal_date + datetime.timedelta(days=31)
        next_to_last = last_bal_date + datetime.timedelta(days=31)

        if target_date > next_to_last:
            return redirect('groupofcompany-ledger', 
                customer = self.kwargs['customer'], 
                month = next_to_last.month, 
                year = next_to_last.year)
        elif target_date < next_to_first:
            return redirect('groupofcompany-ledger', 
                customer = self.kwargs['customer'], 
                month = next_to_first.month, 
                year = next_to_first.year)
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        customer = self.kwargs['customer']
        context['customer'] = GroupofCompany.objects.get(pk=customer)
        month = self.kwargs['month']
        year = self.kwargs['year']
        context['filter_form'] = GroupofCompanyLedgerFilterForm(self.kwargs or None)
        context['month'] = month
        context['year'] = year
        target_date = self.kwargs['target_date']
        prev_date = target_date - datetime.timedelta(days=1)
        next_date = target_date + datetime.timedelta(days=31)
        context['prev'] = prev_date
        context['next'] = next_date
        from_date = datetime.date(year,month,1)
        to_date = CashBalance.objects.filter(date__month=month,date__year=year).order_by('date').last().date
        
        balances = GroupofCompanyBalance.objects.filter(customer=customer, year=prev_date.year, month=prev_date.month)
        if balances.count() == 0:
            context['has_balance'] = False
            return context
        else: balance = balances.last()

        context['balance_bf'] = balance.amount
        context['balance_bf_date'] = datetime.date(year,month,1)
        context['has_balance'] = True
        # Data
        duesells = DueSell.objects.filter(customer__group=customer, date__gte=from_date, date__lte=to_date)
        duecollections = DueCollection.objects.filter(customer__group=customer, date__gte=from_date, date__lte=to_date)
        sub_companies = Customer.objects.filter(group=customer)
        context['sub_companies'] = sub_companies
        
        data = []
        totals = {sub_company:0 for sub_company in sub_companies}
        dates = [obj['date'] for obj in duesells.values("date").distinct()]
        for obj in duecollections.values("date").distinct():
            if obj['date'] not in dates:
                dates.append(obj['date'])

        dates = sorted(dates)
        for date in dates:
            sub_company_data = []
            for sub_company in sub_companies:
                per_company_sells = duesells.filter(date=date,customer=sub_company.pk)
                per_company_amount = per_company_sells.aggregate(Sum('amount'))['amount__sum']
                if per_company_amount:
                    totals[sub_company] += per_company_amount
                sub_company_data.append({
                    # 'instance':sub_company,
                    'sells': per_company_sells,
                    'amount': per_company_amount
                    })
            sells = duesells.filter(date=date)
            collection = duecollections.filter(date=date)
            data_today = {
                'date': date,
                'sub_company_data': sub_company_data,
                'amount': sells.aggregate(Sum("amount"))["amount__sum"] if sells.count() > 0 else False,
                'collection': collection.aggregate(Sum("amount"))["amount__sum"] if collection.count() > 0 else False
            } 
            data.append(data_today)
        
        context['totals'] = totals
        balance = context['balance_bf']
        # data = sorted(data, key=lambda x:x['date'])
        for obj in data:
            if 'amount' in obj:
                balance += obj['amount']
            if 'collection' in obj:
                balance -= obj['collection']
            obj.update({'balance': balance})
        context['qs'] = data

        products = Product.objects.all()
        summary = []
        for product in products:
            prod = duesells.filter(product=product)
            if prod.count() > 0:
                qnt = prod.aggregate(Sum('quantity'))['quantity__sum']
                amount = prod.aggregate(Sum('amount'))['amount__sum']
                summary.append({
                    'product': product,
                    'quantity': qnt,
                    'amount': amount
                })
        context['summary'] = summary
        total_sell = duesells.aggregate(Sum("amount"))['amount__sum']
        total_collection = duecollections.aggregate(Sum("amount"))['amount__sum']
        context['total_sell'] = total_sell or "00"
        context['total_collection'] = total_collection or "00"

        return context

# Customer Balance (Group of company included)
class CustomerBalanceView(LoginRequiredMixin,TemplateView):
    template_name = 'Ledger/customer_balance.html'

    def get(self,request,*args, **kwargs):
        today = datetime.date.today()
        if 'month' in self.request.GET and 'year' in self.request.GET:
                self.kwargs['month'] = int(self.request.GET['month'])
                self.kwargs['year'] = int(self.request.GET['year'])
        elif 'month' not in self.kwargs and 'year' not in self.kwargs:
            if CustomerBalance.objects.exists():
                last_bal_date = CustomerBalance.objects.order_by('year','month').last()
                self.kwargs['month'] = last_bal_date.month
                self.kwargs['year'] = last_bal_date.year
            else:
                self.kwargs['month'] = today.month
                self.kwargs['year'] = today.year
        
        month = int(self.kwargs['month'])
        year = int(self.kwargs['year'])
        
        last_balance= CustomerBalance.objects.order_by('year','month').last()
        first_balance= CustomerBalance.objects.order_by('year','month').first()

        target_date = datetime.date(year,month,1)
        self.kwargs['target_date'] = target_date
        first_balance_date = datetime.date(int(first_balance.year),int(first_balance.month),1)
        last_balance_date = datetime.date(int(last_balance.year),int(last_balance.month),1)
        
        if target_date > last_balance_date:
            return redirect('customer-balance', 
                month = last_balance_date.month, 
                year = last_balance_date.year)
        elif target_date < first_balance_date:
            return redirect('customer-balance', 
                month = first_balance_date.month, 
                year = first_balance_date.year)

        return super().get(request, *args, **kwargs)
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # মাসিক খতিয়ান এর parameter সেট করার জন্য, যেন পরবর্তী মাসে চলে যায়
        month = int(self.kwargs['month'])
        year = int(self.kwargs['year'])
        target_date = self.kwargs['target_date']
        context['month'] = target_date.month
        context['year'] = target_date.year
        prev_date = target_date - datetime.timedelta(days=1)
        next_date = target_date + datetime.timedelta(days=31)
        context['prev'] = prev_date
        context['next'] = next_date
        # Show storage date on heading
        context['date_form'] = DateFilterForm(self.kwargs or None)
        total_current_bal = 0
        total_baddebt = 0

        # First create balances with 0 amount if not exists
        cust_balances = CustomerBalance.objects.filter(
            month=month,year=year, customer__group__isnull=True)
        cust_ids = cust_balances.values('customer_id').distinct()
        unused_customers = Customer.objects.filter(group__isnull=True).exclude(id__in=cust_ids)
        for customer in unused_customers:
            obj = CustomerBalance.objects.create(month=month,year=year,customer=customer,amount=0)
            obj.save()

        # Group of Company - Current
        goc_balances = GroupofCompanyBalance.objects.filter(month=month,year=year, bad_debt=False)
        if goc_balances:
            context['goc_balances'] = goc_balances
            context['goc_balances_count'] = goc_balances.count()
            goc_total = goc_balances.aggregate(Sum('amount'))['amount__sum']
            total_current_bal += goc_total
        else: context['goc_balances_count'] = 0
        # Customer Balances - Current
        cust_balances = CustomerBalance.objects.filter(
            month=month,year=year, customer__group__isnull=True, bad_debt=False)
        if cust_balances:
            context['cust_balances'] = cust_balances
            cust_bal_total = cust_balances.aggregate(Sum('amount'))['amount__sum']
            total_current_bal += cust_bal_total

        # Group of Company - Bad Debts
        goc_baddebts = GroupofCompanyBalance.objects.filter(month=month,year=year, bad_debt=True)
        if goc_baddebts:
            context['goc_baddebts'] = goc_baddebts
            context['goc_baddebts_count'] = goc_baddebts.count()
            goc_baddebt_total = goc_baddebts.aggregate(Sum('amount'))['amount__sum']
            total_baddebt += goc_baddebt_total
        else: context['goc_baddebts_count'] = 0
        # Customer Balances - Bad Debts
        cust_bad_debts = CustomerBalance.objects.filter(
            month=month, year=year, customer__group__isnull=True, bad_debt=True)
        if cust_bad_debts:
            context['cust_bad_debts'] = cust_bad_debts
            total_cust_baddebt = cust_bad_debts.aggregate(Sum('amount'))['amount__sum']
            total_baddebt += total_cust_baddebt
        
        # Totals
        context['total_current_bal'] = total_current_bal
        context['total_baddebt'] = total_baddebt
        context['grand_total'] = total_current_bal + total_baddebt

        context['can_change'] = True
        return context

@login_required
def customerBalanceFormsetView(request,month,year):
    # Group of Company Forms -----------------------------
    goc_balances = GroupofCompanyBalance.objects.all()
    unique_goc = goc_balances.values('customer').annotate(
        total=Count('customer')).filter(total=1).values_list('customer', flat=True)
    unique_goc_bals = goc_balances.filter(customer__in=unique_goc)
    GocBalanceFormset = modelformset_factory(GroupofCompanyBalance, GroupofCompanyBalanceForm, extra=0)
    goc_formset = GocBalanceFormset(request.POST or None, queryset=unique_goc_bals, prefix='goc')
    # Customer Forms -------------------------------------
    cust_balances = CustomerBalance.objects.filter(customer__group__isnull=True)
    # শুধুমাত্র প্রাথমিক ব্যালেন্স পরিবর্তন করা যাবে, বাকি মাসের গুলো auto generate হবে
    unique_customers = cust_balances.values('customer').annotate(
        total=Count('customer')).filter(total=1).values_list('customer', flat=True)
    unique_balances = cust_balances.filter(customer__in=unique_customers)
    CustomerBalanceFormSet = modelformset_factory(CustomerBalance, CustomerBalanceForm, extra=0)
    cust_formset = CustomerBalanceFormSet(request.POST or None, queryset=unique_balances, prefix='cust')
    cust_formset.initial = [{
        'customer':obj.customer,
        'amount':obj.amount, 
        'bad_debt': obj.bad_debt} for obj in unique_balances]
    template = "Ledger/customer_balance_formset.html"
    context = {
        'goc_formset': goc_formset, 'cust_formset': cust_formset, 
        'month': month, 'year':year
        }

    if request.method == 'POST':
        if cust_formset.errors or goc_formset.errors:
            print(cust_formset.errors)
            print(goc_formset.errors)
        if cust_formset.is_valid() and goc_formset.is_valid():
            goc_formset.save()
            cust_formset.save()
            return redirect('customer-balance', month=month, year=year)
    return render(request,template,context)

@login_required
def markBaddebt(requst,month,year,cust_pk,goc=False,unmark=False):
    if goc:
        objects = GroupofCompanyBalance.objects.filter(month__gte=month,year__gte=year,customer=cust_pk)
    else:
        objects = CustomerBalance.objects.filter(month__gte=month,year__gte=year,customer=cust_pk)
    for obj in objects:
        if not unmark:
            obj.bad_debt = True
        else: obj.bad_debt = False
        obj.save()
    return redirect('customer-balance',month=month,year=year)
    
