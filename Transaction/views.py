from django.shortcuts import render, redirect
from django.urls import reverse_lazy
import datetime, calendar
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Sum

from Product.models import Sell, Purchase, StorageReading
from Customer.models import DueSell, DueCollection, Customer
from Expenditure.models import Expenditure
from Revenue.models import Revenue
from Owner.models import Withdraw, Owner, Investment
from .forms import DateForm, CashBalanceForm, CashBalanceForm2
from .models import CashBalance
from Core.choices import last_day_of_month

class DailyTransactionView(TemplateView):
    template_name = "Transaction/daily_transactions.html"

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        date = context['date']
        if 'balance_form' in request.POST:
            if context['balance_form'].is_valid():
                context['balance_form'].save()
                last_date = last_day_of_month(date.year,date.month)
                print(last_date==date)
                if date == last_date:
                    return redirect(reverse_lazy('save-ledger',kwargs={'date':date}))

            return redirect('.', date)
        return super(TemplateView, self).render_to_response(context)
    
    def get(self,request, *args, **kwargs):
        if not CashBalance.objects.exists():
            context = self.get_context_data()
            return super(TemplateView, self).render_to_response(context)
        # In models, CashBalances are ordered by '-date'
        last_balance = CashBalance.objects.order_by('date').last()
        first_balance = CashBalance.objects.order_by('date').first()
        self.kwargs['last_balance'] = last_balance
        
        current_day = last_balance.date + datetime.timedelta(days=1)
        first_day = first_balance.date + datetime.timedelta(days=1)
        # if request with no date, just redirect to next day
        if 'date' not in self.kwargs:
            return redirect('daily-transactions', date=current_day)
        # else
        if 'date_day' in self.request.GET:
            date = datetime.date(int(self.request.GET.get('date_year')),
                int(self.request.GET.get('date_month')),
                int(self.request.GET.get('date_day')))
        elif 'date' in self.kwargs:
            date = self.kwargs['date']

        # Don't let go future
        if date > current_day:
            return redirect('daily-transactions', date=current_day)
        # Don't let go before first date of account starts
        if date < first_day:
            return redirect('daily-transactions', date=first_day)
            
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        
        today = datetime.date.today()
        if 'date_day' in self.request.GET:
            date = datetime.date(
                int(self.request.GET.get('date_year')),
                int(self.request.GET.get('date_month')),
                int(self.request.GET.get('date_day')))
        elif 'date' in self.kwargs:
            date = self.kwargs['date']
        else: date = today
        context['date'] = date
        context['prev_day'] = date - datetime.timedelta(days=1)
        context['next_day'] = date + datetime.timedelta(days=1)
        date_str = date.strftime("%d/%m/%Y")
        context['date_str'] = date_str

        context['active_accounts'] = True
        # If no balance at all, add first
        if not CashBalance.objects.exists():
            context['active_accounts'] = False
            return context
        # date_str = date.strftime("%d %B, %Y")
        context['date_form'] = DateForm(self.request.GET or None, initial={'date':date})

        # Queries
        sells = Sell.objects.filter(date=date)
        duecollections = DueCollection.objects.filter(date=date).order_by('id')
        revenues = Revenue.objects.filter(date=date)
        investments = Investment.objects.filter(date=date)

        purchases = Purchase.objects.filter(date=date)
        # Duesell
        duesells = DueSell.objects.filter(date=date)
        customers = Customer.objects.all()
        duesell_data = []
        for customer in customers:
            cust_duesells = duesells.filter(customer=customer)
            if cust_duesells:
                duesell_data.append({
                    'customer': customer,
                    'due_sells': cust_duesells,
                    'cust_total': cust_duesells.aggregate(Sum('amount'))['amount__sum']
                })

        expenditures = Expenditure.objects.filter(date=date)
        # Withdraws
        withdraws = Withdraw.objects.filter(date=date)
        owners = Owner.objects.all()
        withdraw_data = []
        for owner in owners:
            owner_wds = withdraws.filter(owner=owner)
            if owner_wds:
                withdraw_data.append({
                    'owner': owner, 'withdraws': owner_wds,
                    'owner_total': owner_wds.aggregate(Sum('amount'))['amount__sum']
                })

        storages = StorageReading.objects.filter(date=date)

        context['sells'] = sells
        context['total_sell'] = sells.aggregate(Sum('amount'))['amount__sum']
        context['duecollections'] = duecollections
        context['total_duecollections'] = duecollections.aggregate(Sum('amount'))['amount__sum']
        context['revenues'] = revenues
        context['total_revenues'] = revenues.aggregate(Sum('amount'))['amount__sum']
        context['investments'] = investments
        context['total_investments'] = investments.aggregate(Sum('amount'))['amount__sum']

        context['purchases'] = purchases
        context['total_purchase'] = purchases.aggregate(Sum('amount'))['amount__sum']
        context['duesells'] = duesell_data
        context['total_duesells'] = duesells.aggregate(Sum('amount'))['amount__sum']
        context['expenditures'] = expenditures
        context['total_expenditures'] = expenditures.aggregate(Sum('amount'))['amount__sum']
        context['withdraws'] = withdraw_data
        context['total_withdraws'] = withdraws.aggregate(Sum('amount'))['amount__sum']
        context['storages'] = storages
        
        # Balance B/F
        balances = CashBalance.objects.order_by('date').all()
        balances_lt_date = balances.filter(date__lt=date)
        balance_bf_last = balances_lt_date.last()
        context['balance_bf'] = balance_bf_last.amount
        context['balance_bf_abs'] = abs(balance_bf_last.amount)
        context['balance_bf_date'] = balance_bf_last.date
        if context['balance_bf'] < 0:
            context['balance_bf_side'] = 'credit'
        else: context['balance_bf_side'] = 'debit'
        
        # Balance C/F
        total_debit = 0
        total_credit = 0
        if context['balance_bf'] > 0:
            total_debit += context['balance_bf']
        else: total_credit += context['balance_bf']
        
        if context['total_sell']:
            total_debit += context['total_sell']
        if context['total_duecollections']:
            total_debit += context['total_duecollections']
        if context['total_revenues']:
            total_debit += context['total_revenues']
        if investments: total_debit += context['total_investments']
        context['total_debit'] = total_debit

        if context['total_purchase']:
            total_credit += context['total_purchase']
        if context['total_duesells']:
            total_credit += context['total_duesells']
        if context['total_expenditures']:
            total_credit += context['total_expenditures']
        if context['total_withdraws']:
            total_credit += context['total_withdraws']
        context['total_credit'] = total_credit

        context['balance_cf'] = total_debit - total_credit
        context['balance_cf_abs'] = abs(context['balance_cf'])
        if context['balance_cf'] > 0:
            context['balance_cf_side'] = 'credit'
        else: context['balance_cf_side'] = 'debit'

        saved_balance = balances.filter(date=date)
        if saved_balance.count() > 0:
            context['saved_balance_cf'] = saved_balance.last().amount
            if context['saved_balance_cf'] != context['balance_cf']:
                context['need_update'] = True

        # Limit Editing features
        context['can_change'] = True
        # context['can_change'] = False
        # same day / today
        next_date = balances.last().date + datetime.timedelta(days=1)
        if date == next_date:
            context['can_change'] = True

        context['balance_form'] = CashBalanceForm2(
            self.request.POST or None, 
            initial={'date':date,'amount':context['balance_cf']})
        return context

class CashBalanceListView(ListView):
    model = CashBalance
    ordering = ['-date']
    paginate_by = 20

class CashBalanceCreateView(CreateView):
    model = CashBalance
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'date' in self.kwargs:
            context['date'] = self.kwargs['date']
            context['form'].initial = {'date':context['date'] - datetime.timedelta(days=1)}
        return context

class CashBalanceUpdateView(UpdateView):
    model = CashBalance
    form_class = CashBalanceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = context['form']['date'].initial + datetime.timedelta(days=1)
        return context

class CashBalanceDeleteView(DeleteView):
    model = CashBalance
    success_url = reverse_lazy('cashbalance-list')
    
    # def get_success_url(self):
        # return reverse_lazy('daily-transactions', kwargs={'date':self.object.date})