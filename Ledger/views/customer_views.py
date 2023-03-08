from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView
from django.db.models import Sum
import datetime

from Customer.models import Customer, GroupofCompany, DueSell, DueCollection
from Product.models import Product
from Ledger.models import CustomerBalance, GroupofCompanyBalance, BadDebt
from Ledger.forms import CustomerLedgerFilterForm, GroupofCompanyLedgerFilterForm, DateFilterForm, BadDebtForm
from Transaction.models import CashBalance

class CustomerTopSheet(TemplateView):
    template_name = 'Ledger/customer_topsheet.html'

    def get(self, request, *args, **kwargs):
        # maintain cashbalance date to avoid blank page
        if CashBalance.objects.exists():
            first_bal_date = CashBalance.objects.order_by('date').first().date
            last_bal_date = CashBalance.objects.order_by('date').last().date

            first_date = datetime.date(first_bal_date.year,first_bal_date.month,1)
            first_date = first_date + datetime.timedelta(days=31)
        else:
            return redirect('daily-transactions')

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
                data.update({'prev_balance': last_bal})
                total_prev_bal += last_bal.amount

            duesells = DueSell.objects.filter(date__month=month, date__year=year, customer__group=goc.pk)
            duecollections = DueCollection.objects.filter(date__month=month, date__year=year, customer__group=goc.pk)

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
            
            baddebts = BadDebt.objects.filter(customer__group=goc.pk)
            baddebt = baddebts.aggregate(Sum('amount'))['amount__sum'] if baddebts else 0
            data['baddebt'] = baddebt

            bal = 0
            bal += data['prev_balance'].amount if data['prev_balance'] else 0
            bal += data['duesell'] - data['duecollection'] - baddebt
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
            
            baddebts = BadDebt.objects.filter(customer=customer.pk, month=month)
            baddebt = baddebts.aggregate(Sum('amount'))['amount__sum'] if baddebts else 0
            data['baddebt'] = baddebt
            bal = 0
            last_bal = data['prev_balance'].amount if data['prev_balance'] else 0
            bal += last_bal
            # কোনো কার্যকলাপ না থাকলে টপশিটে আসবে না
            if last_bal == 0 and due_amount == 0 and collection == 0:
                continue
            
            bal += data['duesell'] - data['duecollection'] - baddebt
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

class CustomerLedger(TemplateView):
    template_name = 'Ledger/customer.html'

    def get(self, request, *args, **kwargs):
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

        context['filter_form'] = CustomerLedgerFilterForm(self.kwargs or None)
        context['customer'] = Customer.objects.get(pk=customer)
        balances = CustomerBalance.objects.filter(customer=customer, year=prev_date.year, month=prev_date.month)
        # if balances.count() == 0:
            # context['has_balance'] = False
            # return context
        #     balance = None
        # else: balance = balances.last()

        context['balance_bf'] = balances.last().amount if balances else 0
        context['balance_bf_date'] = datetime.date(year,month,1)
        context['has_balance'] = True
        # Data
        duesells = DueSell.objects.filter(customer=customer, date__year=year, date__month=month)
        duecollections = DueCollection.objects.filter(customer=customer, date__year=year, date__month=month)
        
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
            
            # diesel = sells.filter(product__name="ডিজেল")
            # if diesel.count() > 0:
            #     d_qnt = diesel.aggregate(Sum('quantity'))['quantity__sum']
            #     total_diesel += d_qnt
            #     data_today.update({'diesel': d_qnt, 'total_diesel': total_diesel})
            
            # others = sells.exclude(product__name="ডিজেল")
            # if others.count() > 0:
            #     o_amount = others.aggregate(Sum('amount'))['amount__sum']
            #     data_today.update({'others': o_amount})
                
            data.append(data_today)
        
        baddebts = BadDebt.objects.filter(customer=customer, month=month)
        baddebt = baddebts.aggregate(Sum('amount'))['amount__sum'] if baddebts else 0
        context['baddebt'] = baddebt
        
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
        context['total_sell'] = total_sell
        context['total_collection'] = total_collection
        context['balance_cf'] = context['balance_bf'] + total_sell - total_collection - baddebt
        return context

class GroupofCompanyLedger(TemplateView):
    template_name = 'Ledger/groupofcompany.html'

    def get(self, request, *args, **kwargs):
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
        
        balances = GroupofCompanyBalance.objects.filter(customer=customer, year=prev_date.year, month=prev_date.month)
        if balances.count() == 0:
            context['has_balance'] = False
            return context
        else: balance = balances.last()

        context['balance_bf'] = balance.amount
        context['balance_bf_date'] = datetime.date(year,month,1)
        context['has_balance'] = True
        # Data
        duesells = DueSell.objects.filter(customer__group=customer, date__year=year, date__month=month)
        duecollections = DueCollection.objects.filter(customer__group=customer, date__year=year, date__month=month)
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

# Customer
class CustomerBalanceView(CreateView, ListView):
    model = CustomerBalance
    fields = '__all__'
    template_name = 'Ledger/customer_balance.html'

    def get(self,request,*args, **kwargs):
        today = datetime.date.today()
        if 'month' not in self.kwargs and 'year' not in self.kwargs:
            if CustomerBalance.objects.exists():
                # first_bal_date = CustomerBalance.objects.first()
                # self.kwargs['month'] = first_bal_date.month
                # self.kwargs['year'] = first_bal_date.year
                last_bal_date = CustomerBalance.objects.last()
                self.kwargs['month'] = last_bal_date.month
                self.kwargs['year'] = last_bal_date.year
            # elif 'month' in self.request.GET and 'year' in self.request.GET:
            #     self.kwargs['month'] = int(self.request.GET['month'])
            #     self.kwargs['year'] = int(self.request.GET['year'])
            else:
                self.kwargs['month'] = today.month
                self.kwargs['year'] = today.year
        
        # month = int(self.kwargs['month'])
        # year = int(self.kwargs['year'])
        
        # last_balance= CustomerBalance.objects.last()
        # first_balance= CustomerBalance.objects.first()

        # target_date = datetime.date(year,month,1)
        # self.kwargs['target_date'] = target_date
        # first_balance_date = datetime.date(int(first_balance.year),int(first_balance.month),1)
        # last_balance_date = datetime.date(int(last_balance.year),int(last_balance.month),1)
        # next_to_first = first_balance_date + datetime.timedelta(days=31)
        # next_to_last = last_balance_date + datetime.timedelta(days=31)
        
        # if target_date > next_to_last:
        #     return redirect('customer-balance', 
        #         month = next_to_last.month, 
        #         year = next_to_last.year)
        # elif target_date < next_to_first:
        #     return redirect('customer-balance', 
        #         month = next_to_first.month, 
        #         year = next_to_first.year)

        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        month = self.kwargs['month']
        year = self.kwargs['year']
        qs = self.model.objects.filter(month=month, year=year)
        return qs

    def get_success_url(self):
        return reverse_lazy('customer-balance', kwargs=self.kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        month = form.cleaned_data['month']
        year = form.cleaned_data['year']
        return redirect(reverse_lazy('customer-balance', kwargs={'month':month, 'year':year}))
    
    def form_invalid(self, form):
        self.object_list = self.get_queryset()
        messages.error(self.request, "এক পার্টির ব্যাল্যান্স মাসে একবারই লিপিবদ্ধ হয়!")
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_initial(self):
        initial = super().get_initial()
        initial.update(self.kwargs)
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # মাসিক খতিয়ান এর parameter সেট করার জন্য, যেন পরবর্তী মাসে চলে যায়
        month = int(self.kwargs['month'])
        year = int(self.kwargs['year'])
        date = datetime.datetime(year,month,1)
        target_date = date + datetime.timedelta(days=31)
        context['month'] = target_date.month
        context['year'] = target_date.year
        # target_date = self.kwargs['target_date']
        # prev_date = target_date - datetime.timedelta(days=1)
        # next_date = target_date + datetime.timedelta(days=31)
        # context['prev'] = prev_date
        # context['next'] = next_date
        # Show storage date on heading
        # context['date_form'] = DateFilterForm(self.kwargs or None)
        context['due_month'] = month
        context['due_year'] = year
        qs = self.get_queryset()
        if qs:
            context['total'] = qs.aggregate(Sum('amount'))['amount__sum']
        return context

def deleteCustomerBalance(request, pk):
    obj = CustomerBalance.objects.get(pk=pk)
    obj.delete()
    return redirect('customer-balance')

# Group of company
class GroupofCompanyBalanceView(CreateView, ListView):
    model = GroupofCompanyBalance
    fields = '__all__'
    paginate_by = 30
    template_name = 'Ledger/groupofcompany_balance.html'

    def get_success_url(self):
        return reverse_lazy('groupofcompany-balance', kwargs=self.kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        month = form.cleaned_data['month']
        year = form.cleaned_data['year']
        return redirect(reverse_lazy('groupofcompany-balance', kwargs={'month':month, 'year':year}))
    
    def form_invalid(self, form):
        self.object_list = self.get_queryset()
        messages.error(self.request, "এক পার্টির ব্যাল্যান্স মাসে একবারই লিপিবদ্ধ হয়!")
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_initial(self):
        initial = super().get_initial()
        initial.update(self.kwargs)
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # মাসিক খতিয়ান এর parameter সেট করার জন্য, যেন পরবর্তী মাসে চলে যায়
        if 'month' in self.kwargs and 'year' in self.kwargs:
            month = int(self.kwargs['month'])
            year = int(self.kwargs['year'])
            date = datetime.datetime(year,month,1)
            target_date = date + datetime.timedelta(days=31)
            context['month'] = target_date.month
            context['year'] = target_date.year
        return context

def deleteGroupofCompanyBalance(request, pk):
    obj = CustomerBalance.objects.get(pk=pk)
    obj.delete()
    return redirect('groupofcompany-balance')

class BadDebtView(CreateView, ListView):
    model = BadDebt
    form_class = BadDebtForm
    template_name = 'Ledger/bad_debt.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if response.status_code == 302:
            customer = form.cleaned_data['customer']
            # balances = CustomerBalance.objects.filter(customer=customer)
            # if balances:
            #     balance = balances.first()
            #     balance.amount -= form.cleaned_data['amount']
            #     balance.save()
            disable_customer = form.cleaned_data['disable_customer']
            if disable_customer:
                customer.status = 'inactive'
                customer.save()

        return redirect(reverse_lazy('baddebt'))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total'] = self.model.objects.aggregate(Sum('amount'))['amount__sum']
        return context

def deleteBadDebt(request, pk):
    obj = BadDebt.objects.get(pk=pk)
    obj.delete()
    return redirect('baddebt')
