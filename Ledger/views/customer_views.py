from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView
from django.db.models import Sum
import datetime

from Customer.models import Customer, GroupofCompany, DueSell, DueCollection
from Product.models import Product
from Ledger.models import CustomerBalance, GroupofCompanyBalance
from Ledger.forms import CustomerLedgerFilterForm, GroupofCompanyLedgerFilterForm

class CustomerLedger(TemplateView):
    template_name = 'Ledger/customer.html'

    def get(self, request, *args, **kwargs):
        today = datetime.date.today()
        # pk
        if 'customer' in self.request.GET:
            self.kwargs['pk'] = self.request.GET.get('customer')
        elif 'pk' not in self.kwargs:
            self.kwargs['pk'] = Customer.objects.filter(cust_type='Individual').first().pk
        # Month and year
        if 'month' in self.request.GET and 'year' in self.request.GET:
            self.kwargs['month'] = int(self.request.GET.get('month'))
            self.kwargs['year'] = int(self.request.GET.get('year'))
        elif 'month' not in self.kwargs and 'year' not in self.kwargs:
            self.kwargs['month'] = today.month
            self.kwargs['year'] = today.year

        pk = self.kwargs['pk']
        month = self.kwargs['month']
        year = self.kwargs['year']

        balances = CustomerBalance.objects.filter(customer=pk)
        if balances.count() == 0:
            context = self.get_context_data()
            return super(TemplateView, self).render_to_response(context)

        last_balance = balances.last()
        first_balance = balances.first()

        target_date = datetime.date(year,month,1)
        first_bal_date = datetime.date(int(first_balance.year), int(first_balance.month),1)
        last_bal_date = datetime.date(int(last_balance.year), int(last_balance.month),1)
        next_to_first = first_bal_date + datetime.timedelta(days=31)
        next_to_last = last_bal_date + datetime.timedelta(days=31)

        if target_date > next_to_last:
            return redirect('customer-ledger', 
                pk = self.kwargs['pk'], 
                month = next_to_last.month, 
                year = next_to_last.year)
        elif target_date < next_to_first:
            return redirect('customer-ledger', 
                pk = self.kwargs['pk'], 
                month = next_to_first.month, 
                year = next_to_first.year)

        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        pk = self.kwargs['pk']
        month = self.kwargs['month']
        year = self.kwargs['year']

        context['filter_form'] = CustomerLedgerFilterForm(self.request.GET or None)
        context['filter_form'].initial = {'customer':pk,'month':month,'year':year}
        context['month'] = month
        context['year'] = year
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
        context['balance_bf_date'] = datetime.date(year,month,1)
        context['has_balance'] = True
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
            diesel = sells.filter(product__name="ডিজেল")
            # print(diesel)
            if diesel.count() > 0:
                d_qnt = diesel.aggregate(Sum('quantity'))['quantity__sum']
                total_diesel += d_qnt
                data_today.update({'diesel': d_qnt, 'total_diesel': total_diesel})
            others = sells.exclude(product__name="ডিজেল")
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
        return context

class GroupofCompanyLedger(TemplateView):
    template_name = 'Ledger/groupofcompany.html'

    def get(self, request, *args, **kwargs):
        today = datetime.date.today()
        # pk
        if 'customer' in self.request.GET:
            self.kwargs['pk'] = self.request.GET.get('customer')
        elif 'pk' not in self.kwargs:
            self.kwargs['pk'] = GroupofCompany.objects.first().pk
        # Month and year
        if 'month' in self.request.GET and 'year' in self.request.GET:
            self.kwargs['month'] = int(self.request.GET.get('month'))
            self.kwargs['year'] = int(self.request.GET.get('year'))
        elif 'month' not in self.kwargs and 'year' not in self.kwargs:
            self.kwargs['month'] = today.month
            self.kwargs['year'] = today.year

        pk = self.kwargs['pk']
        month = self.kwargs['month']
        year = self.kwargs['year']

        balances = GroupofCompanyBalance.objects.filter(customer=pk)
        if balances.count() == 0:
            context = self.get_context_data()
            return super(TemplateView, self).render_to_response(context)

        last_balance = balances.last()
        first_balance = balances.first()

        target_date = datetime.date(year,month,1)
        first_bal_date = datetime.date(int(first_balance.year), int(first_balance.month),1)
        last_bal_date = datetime.date(int(last_balance.year), int(last_balance.month),1)
        next_to_first = first_bal_date + datetime.timedelta(days=31)
        next_to_last = last_bal_date + datetime.timedelta(days=31)

        if target_date > next_to_last:
            return redirect('groupofcompany-ledger', 
                pk = self.kwargs['pk'], 
                month = next_to_last.month, 
                year = next_to_last.year)
        elif target_date < next_to_first:
            return redirect('groupofcompany-ledger', 
                pk = self.kwargs['pk'], 
                month = next_to_first.month, 
                year = next_to_first.year)
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        pk = self.kwargs['pk']
        self.kwargs['customer'] = pk
        month = self.kwargs['month']
        year = self.kwargs['year']
        context['filter_form'] = GroupofCompanyLedgerFilterForm(self.request.GET or self.kwargs or None)
        context['month'] = month
        context['year'] = year
        context['prev'] = {
            'month': month - 1 if month > 1 else 12,
            'year': year if month > 1 else year - 1
        }
        context['next'] = {
            'month': month + 1 if month < 12 else 1,
            'year': year  if month < 12 else year + 1
        }
        context['customer'] = GroupofCompany.objects.get(pk=pk)
        balances = GroupofCompanyBalance.objects.filter(customer=pk)
        if balances.count() == 0:
            context['has_balance'] = False
            return context
        else: balance = balances.last()

        context['balance_bf'] = balance.amount
        context['balance_bf_date'] = datetime.date(year,month,1)
        context['has_balance'] = True
        # Data
        duesells = DueSell.objects.filter(customer__group=pk, date__year=year, date__month=month)
        duecollections = DueCollection.objects.filter(customer__group=pk, date__year=year, date__month=month)
        sub_companies = Customer.objects.filter(group=pk)
        context['sub_companies'] = sub_companies
        
        data = []
        totals = {sub_company:0 for sub_company in sub_companies}
        dates = [obj['date'] for obj in duesells.values("date").distinct()]
        for obj in duecollections.values("date").distinct():
            if obj['date'] not in dates:
                dates.append(obj['date'])

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
        if CustomerBalance.objects.exists():
            # first_bal_date = Storage.objects.first().date
            last_bal_date = CustomerBalance.objects.last()
            self.kwargs['month'] = last_bal_date.month
            self.kwargs['year'] = last_bal_date.year
        # elif 'month' in self.request.GET and 'year' in self.request.GET:
        #     self.kwargs['month'] = int(self.request.GET['month'])
        #     self.kwargs['year'] = int(self.request.GET['year'])
        elif 'month' not in self.kwargs and 'year' not in self.kwargs:
            self.kwargs['month'] = today.month
            self.kwargs['year'] = today.year

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
        # Show storage date on heading
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
