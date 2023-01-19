from django.shortcuts import render, HttpResponse, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Sum
import pybengali
import datetime
from itertools import chain

from Customer.models import Customer, GroupofCompany, DueSell, DueCollection
from Product.models import Product, ProductGroup
from Expenditure.models import ExpenditureGroup
from Revenue.models import RevenueGroup
from Transaction.models import CashBalance
from .models import CustomerBalance, GroupofCompanyBalance
from .forms import CustomerLedgerFilterForm

class LedgerList(TemplateView):
    template_name = 'Ledger/ledger_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Party
        group_of_companies = GroupofCompany.objects.all()
        customers = Customer.objects.all()
        customer_dataset = []
        goc = customers.filter(cust_type='Group')
        for company in group_of_companies:
            customer_dataset.append(
                {'name': company, 'companies': goc.filter(group=company)}
            )
        context['group_cumtomer'] = customer_dataset
        context['individual_customer'] = customers.filter(cust_type='Individual')
        
        # Others
        context['product_group'] = ProductGroup.objects.all()
        context['expenditure_group'] = ExpenditureGroup.objects.all()
        context['revenue_group'] = RevenueGroup.objects.all()
        
        return context

class CustomerLedger(TemplateView):
    template_name = 'Ledger/customer.html'

    def get(self, request, *args, **kwargs):
        today = datetime.date.today()
        # pk
        if 'customer' in self.request.GET:
            pk = self.request.GET.get('customer')
        elif 'pk' in self.kwargs:
            pk = self.kwargs['pk']
        else: pk = 1
        # Month
        if 'month' in self.request.GET:
            month = int(self.request.GET.get('month'))
        elif 'month' in self.kwargs:
            month = int(self.kwargs['month'])
        else: month = today.month
        # Year
        if 'year' in self.request.GET:
            year = int(self.request.GET.get('year'))
        elif 'year' in self.kwargs:
            year = int(self.kwargs['year'])
        else: year = today.year

        self.kwargs['pk'] = pk
        self.kwargs['month'] = month
        self.kwargs['year'] = year

        balances = CustomerBalance.objects.filter(customer=pk)
        if balances.count() == 0:
            context = self.get_context_data()
            return super(TemplateView, self).render_to_response(context)

        last_balance = balances.last()
        first_balance = balances.first()

        lb_month = int(last_balance.month)
        # lb_year = int(last_balance.year)
        fb_month = int(first_balance.month)
        # fb_year = int(last_balance.year)
        current_month = lb_month + 1 if lb_month < 12 else 1
        current_year = last_balance.year if lb_month < 12 else last_balance.year + 1
        first_month = fb_month + 1 if fb_month < 12 else 1
        first_year = last_balance.year if lb_month < 12 else last_balance.year + 1
        self.kwargs['current_month'] = current_month
        self.kwargs['current_year'] = current_year
        # if request with no date, just redirect to next day
        # if 'month' not in self.kwargs:
        #     return redirect('customer-ledger', pk=self.kwargs['pk'], month=current_month, year=current_year)


        # Don't let go future
        if month > current_month or year > current_year:
            return redirect('customer-ledger', pk=pk, month=current_month, year=current_year)
        # Don't let go before first date of account starts
        if month < first_month or year < first_year:
            return redirect('customer-ledger', pk=pk, month=first_month, year=first_year)
            
        # end
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        pk = self.kwargs['pk']
        month = self.kwargs['month']
        year = self.kwargs['year']
        context['filter_form'] = CustomerLedgerFilterForm(self.request.GET or None)
        context['filter_form'].initial = {'customer':pk,'month':month,'year':year}
        context['month'] = pybengali.eng_month_to_bengali(month)
        context['year'] = pybengali.convert_e2b_digit(year)
        context['prev'] = {
            'month': month - 1 if month > 1 else 12,
            'year': year if month > 1 else year - 1
        }
        context['next'] = {
            'month': month + 1 if month < 12 else 1,
            'year': year  if month < 12 else year + 1
        }
        context['customer'] = Customer.objects.get(pk=pk)
        balances = CustomerBalance.objects.filter(customer=pk)
        if balances.count() == 0:
            context['has_balance'] = False
            return context
        else: balance = balances.last()

        context['balance_bf'] = balance.amount
        context['balance_bf_date'] = datetime.date(day=1,
            month=self.kwargs['current_month'],
            year=self.kwargs['current_year'])
        context['has_balance'] = True

        balance_cf_date = datetime.date(day=1,
            month = context['next']['month'],
            year = context['next']['year']) - datetime.timedelta(days=1)
        
        # Data
        duesells = DueSell.objects.filter(customer=pk, date__year=year, date__month=month)
        duecollections = DueCollection.objects.filter(customer=pk, date__year=year, date__month=month)
        
        data = []
        dates = [obj['date'] for obj in duesells.values("date").distinct()]
        for obj in duecollections.values("date").distinct():
            if obj['date'] not in dates:
                dates.append(obj['date'])

        total_diesel = 0
        for date in dates:
            sells = duesells.filter(date=date)
            collection = duecollections.filter(date=date)
            data_today = {
                'date': date,
                'sells': sells,
                'amount': sells.aggregate(Sum("amount"))["amount__sum"] if sells.count() > 0 else False,
                'collection': collection.aggregate(Sum("amount"))["amount__sum"] if collection.count() > 0 else False
            }
            diesel = sells.filter(product__item__name="ডিজেল")
            # print(diesel)
            if diesel.count() > 0:
                d_qnt = diesel.aggregate(Sum('quantity'))['quantity__sum']
                total_diesel += d_qnt
                data_today.update({'diesel': d_qnt, 'total_diesel': total_diesel})
            others = sells.exclude(product__item__name="ডিজেল")
            # print(others)
            if others.count() > 0:
                o_amount = others.aggregate(Sum('amount'))['amount__sum']
                data_today.update({'others': o_amount})
                
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
        total_sell = duesells.aggregate(Sum("amount"))['amount__sum']
        total_collection = duecollections.aggregate(Sum("amount"))['amount__sum']
        context['total_sell'] = total_sell or "00"
        context['total_collection'] = total_collection or "00"

        # Autosave balance
        # balance_cf_date = last day of month
        cash_balance = CashBalance.objects.filter(date=balance_cf_date)
        if cash_balance.count() == 1:
            customer_balance, created = CustomerBalance.objects.get_or_create(
                month = month, year = year, 
                customer = context['customer'],
                amount = balance
            )
            if created:
                print("Ledger Saved Successfully")
        else: print("Ledger will be saved after saving daily transaction of the last day of this month.")

        return context


# Customer
class CustomerBalanceView(CreateView, ListView):
    model = CustomerBalance
    fields = '__all__'
    template_name = 'Ledger/customer_balance.html'
    success_url = '.'

    def get_initial(self):
        initial = super().get_initial()
        if 'cust_id' in self.kwargs:
            initial.update({'customer':self.kwargs['cust_id']})
        return initial

def deleteCustomerBalance(request, pk):
    obj = CustomerBalance.objects.get(pk=pk)
    obj.delete()
    return redirect('customer-balance')

# Group of company
class GroupofCompanyBalanceView(CreateView, ListView):
    model = GroupofCompanyBalance
    fields = '__all__'
    template_name = 'Ledger/groupofcompany_balance.html'
    success_url = '.'

    def get_initial(self):
        initial = super().get_initial()
        if 'cust_id' in self.kwargs:
            initial.update({'customer':self.kwargs['cust_id']})
        return initial

def deleteGroupofCompanyBalance(request, pk):
    obj = CustomerBalance.objects.get(pk=pk)
    obj.delete()
    return redirect('groupofcompany-balance')