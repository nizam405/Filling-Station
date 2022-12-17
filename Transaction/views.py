from django.shortcuts import render, redirect
from django.urls import reverse_lazy
import datetime
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.db.models import Sum

from Product.models import Sell, Purchase
from Customer.models import DueSell, DueCollection
from Expenditure.models import Expenditure
from Revenue.models import Revenue
from Owner.models import Withdraw
from .forms import DateForm, CashBalanceForm, CashBalanceForm2
from .models import CashBalance

class DailyTransactionView(TemplateView):
    template_name = "Transaction/daily_transactions.html"

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        
        if context['need_update']:
            balances = CashBalance.objects.filter(date__gte=context['date'])
            diff = context['balance_cf'] - context['saved_balance_cf']
            for balance in balances:
                balance.amount = balance.amount + diff
                balance.save()
                return redirect('.', args={'date':context['date']})
        else:
            if context['balance_form'].is_valid():
                context['balance_form'].save()
            return redirect('.', args={'date':context['date']})
        return super(TemplateView, self).render_to_response(context)
    
    def get(self,request, *args, **kwargs):
        # Don't let go future
        today = datetime.date.today()
        if self.kwargs['date'] > today:
            return redirect('daily-transactions', date=today)

        balances = CashBalance.objects.all()
        last_balance = balances.last()
        first_balance = balances.first()
        # If queryset has any balance (example: last_balance)
        if balances.count() > 0:
            next_day = last_balance.date + datetime.timedelta(days=1)
            first_day = first_balance.date + datetime.timedelta(days=1)
            # if request with no date, just redirect to next day
            if 'date' not in self.kwargs:
                return redirect('daily-transactions', date=next_day)
            # else
            day = self.kwargs['date']
            # Allow next day and only dates that has data saved
            if day > next_day or day < first_day:
                return redirect('daily-transactions', date=next_day)

        return super().get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['need_update'] = False
        today = datetime.date.today()
        if 'date_day' in self.request.GET:
            date = datetime.date(int(self.request.GET.get('date_year')),
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
        # date_str = date.strftime("%d %B, %Y")
        context['date_form'] = DateForm(self.request.GET or None, initial={'date':date})

        # Get previous balances only
        balances = CashBalance.objects.all()
        balances_lt_date = balances.filter(date__lt=date)
        # If doesn't have any balance, let add balance first
        # else show stuff
        if balances.count() == 0:
            context['active_accounts'] = False
        else:
            # if balance_bf_last.count() == 0:
            #     return redirect()
            context['active_accounts'] = True
            balance_bf_last = balances_lt_date.last()

            # Queries
            sells = Sell.objects.filter(date=date)
            duecollections = DueCollection.objects.filter(date=date)
            revenues = Revenue.objects.filter(date=date)

            purchases = Purchase.objects.filter(date=date)
            duesells = DueSell.objects.filter(date=date)
            expenditures = Expenditure.objects.filter(date=date)
            withdraws = Withdraw.objects.filter(date=date)

            context['sells'] = sells
            context['total_sell'] = sells.aggregate(Sum('amount'))['amount__sum']
            context['duecollections'] = duecollections
            context['total_duecollections'] = duecollections.aggregate(Sum('amount'))['amount__sum']
            context['revenues'] = revenues
            context['total_revenues'] = revenues.aggregate(Sum('amount'))['amount__sum']

            context['purchases'] = purchases
            context['total_purchase'] = purchases.aggregate(Sum('amount'))['amount__sum']
            context['duesells'] = duesells
            context['total_duesells'] = duesells.aggregate(Sum('amount'))['amount__sum']
            context['expenditures'] = expenditures
            context['total_expenditures'] = expenditures.aggregate(Sum('amount'))['amount__sum']
            context['withdraws'] = withdraws
            context['total_withdraws'] = withdraws.aggregate(Sum('amount'))['amount__sum']
            
            # Balance B/F
            context['balance_bf'] = balance_bf_last.amount
            context['balance_bf_abs'] = abs(balance_bf_last.amount)
            context['balance_bf_date'] = balance_bf_last.date.strftime("%d/%m/%Y")
            if context['balance_bf'] < 0:
                context['balance_bf_side'] = 'credit'
            else: context['balance_bf_side'] = 'debit'
            
            # Balance C/F
            total_debit = 0.0
            total_credit = 0.0
            if context['balance_bf'] > 0:
                total_debit += context['balance_bf']
            else: total_credit += context['balance_bf']
            
            if context['total_sell']:
                total_debit += context['total_sell']
            if context['total_duecollections']:
                total_debit += context['total_duecollections']
            if context['total_revenues']:
                total_debit += context['total_revenues']
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
            context['can_save'] = False
            context['can_update'] = False
            # same day / today
            if date == balances.last().date + datetime.timedelta(days=1):
                context['can_update'] = True
                context['can_save'] = True
            # prev day
            elif date == balances.last().date:
                context['can_save'] = False
                context['can_update'] = False
                # context['can_update'] = True
            # elif date < balances.last().date:
            #     context['can_save'] = False
            #     context['can_update'] = False
                # if 'saved_balance_cf' not in context and balance_bf_last.date == context['prev_day']:
                #     context['can_change'] = True

            context['balance_form'] = CashBalanceForm2(
                self.request.POST or None, 
                initial={'date':date,'amount':context['balance_cf']})
        return context


class CashBalanceListView(ListView):
    model = CashBalance
    fields = '__all__'

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