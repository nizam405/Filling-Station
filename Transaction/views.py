from django.shortcuts import render, redirect
from django.urls import reverse_lazy
import datetime
from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin

from Product.models import Sell, Purchase, StorageReading
from Customer.models import DueSell, DueCollection, Customer
from Expenditure.models import Expenditure
from Revenue.models import Revenue
from Owner.models import Withdraw, Owner, Investment
from Product.models import Product
from Loan.models import BorrowLoan, LendLoan, RefundLendedLoan, RefundBorrowedLoan
from .forms import DateForm, CashBalanceForm, CashBalanceForm2, CashBalanceControlForm
from .models import CashBalance
from .functions import save_cashbalance, last_balance_date

class DailyTransactionView(LoginRequiredMixin,TemplateView):
    template_name = "Transaction/daily_transactions.html"

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        date = context['date']
        if 'balance_form' in request.POST:
            if context['balance_form'].is_valid():
                context['balance_form'].save()
                date += datetime.timedelta(days=1)

            return redirect('daily-transactions', date)
        return super(TemplateView, self).render_to_response(context)
    
    def get(self,request, *args, **kwargs):
        if not CashBalance.objects.exists():
            context = self.get_context_data()
            return super(TemplateView, self).render_to_response(context)
        
        last_balance_date = CashBalance.objects.latest().date
        first_balance_date = CashBalance.objects.earliest().date
        # self.kwargs['last_balance'] = last_balance
        
        current_day = last_balance_date + datetime.timedelta(days=1)
        first_day = first_balance_date + datetime.timedelta(days=1)
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
        # If no balance at all, add first
        if not CashBalance.objects.exists():
            return context
        # date_str = date.strftime("%d %B, %Y")
        context['date_form'] = DateForm(self.request.GET or None, initial={'date':date})

        # Queries
        sells = Sell.objects.filter(date=date)
        duecollections = DueCollection.objects.filter(date=date).order_by('id')
        revenues = Revenue.objects.filter(date=date)
        investments = Investment.objects.filter(date=date)
        # হাওলাদ গ্রহণ
        borrowed_loans = BorrowLoan.objects.filter(date=date)
        # প্রদত্ত হাওলাদ ফেরত
        refund_lended_loans = RefundLendedLoan.objects.filter(date=date)

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
        
        # হাওলাদ প্রদান
        lended_loans = LendLoan.objects.filter(date=date)
        # গৃহীত হাওলাদ পরিশোধ
        refund_borrowed_loans = RefundBorrowedLoan.objects.filter(date=date)

        context['sells'] = sells
        context['total_sell'] = sells.aggregate(Sum('amount'))['amount__sum']
        context['duecollections'] = duecollections
        context['total_duecollections'] = duecollections.aggregate(Sum('amount'))['amount__sum']
        context['revenues'] = revenues
        context['total_revenues'] = revenues.aggregate(Sum('amount'))['amount__sum']
        context['investments'] = investments
        context['total_investments'] = investments.aggregate(Sum('amount'))['amount__sum']
        context['borrowed_loans'] = borrowed_loans
        context['total_borrowed_loan'] = borrowed_loans.aggregate(Sum('amount'))['amount__sum']
        context['refund_lended_loans'] = refund_lended_loans
        context['total_refund_lended_loan'] = refund_lended_loans.aggregate(Sum('amount'))['amount__sum']

        context['purchases'] = purchases
        context['total_purchase'] = purchases.aggregate(Sum('amount'))['amount__sum']
        context['duesells'] = duesell_data
        context['total_duesells'] = duesells.aggregate(Sum('amount'))['amount__sum']
        context['expenditures'] = expenditures
        context['total_expenditures'] = expenditures.aggregate(Sum('amount'))['amount__sum']
        context['withdraws'] = withdraw_data
        context['total_withdraws'] = withdraws.aggregate(Sum('amount'))['amount__sum']
        context['lended_loans'] = lended_loans
        context['total_lended_loan'] = lended_loans.aggregate(Sum('amount'))['amount__sum']
        context['refund_borrowed_loans'] = refund_borrowed_loans
        context['total_refund_borrowed_loan'] = refund_borrowed_loans.aggregate(Sum('amount'))['amount__sum']
        
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
        
        if context['total_sell']: total_debit += context['total_sell']
        if context['total_duecollections']: total_debit += context['total_duecollections']
        if context['total_revenues']: total_debit += context['total_revenues']
        if investments: total_debit += context['total_investments']
        if borrowed_loans: total_debit += context['total_borrowed_loan']
        if refund_lended_loans: total_debit += context['total_refund_lended_loan']
        context['total_debit'] = total_debit

        if context['total_purchase']: total_credit += context['total_purchase']
        if context['total_duesells']: total_credit += context['total_duesells']
        if context['total_expenditures']: total_credit += context['total_expenditures']
        if context['total_withdraws']: total_credit += context['total_withdraws']
        if lended_loans: total_credit += context['total_lended_loan']
        if refund_borrowed_loans: total_credit += context['total_refund_borrowed_loan']
        context['total_credit'] = total_credit

        context['balance_cf'] = total_debit - total_credit
        context['balance_cf_abs'] = abs(context['balance_cf'])
        if context['balance_cf'] > 0:
            context['balance_cf_side'] = 'credit'
        else: context['balance_cf_side'] = 'debit'

        # Edit করার persmission দেয়া হলে, পূর্বের ব্যালেন্স এর সাথে তুলনা করবে
        # context['need_update'] = False
        saved_balance = balances.filter(date=date)
        if saved_balance.count() > 0:
            context['saved_balance_cf'] = saved_balance.last().amount
            # if context['saved_balance_cf'] != context['balance_cf']:
            #     context['need_update'] = True

        # Limit Editing features
        # context['can_change'] = True
        context['can_change'] = False
        # same day / today
        next_date = balances.last().date + datetime.timedelta(days=1)
        if date == next_date:
            context['can_change'] = True

        context['balance_form'] = CashBalanceForm2(
            self.request.POST or None, 
            initial={'date':date,'amount':context['balance_cf']})
        
        storage_readings = StorageReading.objects.filter(date=date)
        count_rescale_products = Product.objects.filter(need_rescale=True).count()
        context['storage_readings'] = storage_readings
        context['need_rescale'] = bool(count_rescale_products)
        context['can_save'] = False
        if count_rescale_products == storage_readings.count():
            context['can_save'] = True

        return context

class CashBalanceListView(LoginRequiredMixin,ListView):
    model = CashBalance
    ordering = ['-date']
    paginate_by = 30

class CashBalanceCreateView(LoginRequiredMixin,CreateView):
    model = CashBalance
    form_class = CashBalanceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'date' in self.kwargs:
            context['date'] = self.kwargs['date']
            context['form'].initial = {'date':context['date'] - datetime.timedelta(days=1)}
        return context

class CashBalanceUpdateView(LoginRequiredMixin,UpdateView):
    model = CashBalance
    form_class = CashBalanceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = context['form']['date'].initial + datetime.timedelta(days=1)
        return context

class CashBalanceDeleteView(LoginRequiredMixin,DeleteView):
    model = CashBalance
    success_url = reverse_lazy('cashbalance-list')
    
class CashBalanceControlView(LoginRequiredMixin, FormView):
    form_class = CashBalanceControlForm
    template_name = 'Transaction/cashbalance_control_form.html'
    success_url = reverse_lazy('daily-transactions')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        to_date = last_balance_date()
        from_date = last_balance_date() + datetime.timedelta(days=1)
        kwargs['initial'] = {'from_date':from_date, 'to_date':to_date}
        return kwargs

    def form_valid(self, form):
        from_date = form.cleaned_data['from_date']
        to_date = form.cleaned_data['to_date']
        action = form.cleaned_data['action']
        date = from_date
        if action == 'save':
            while date <= to_date:
                save_cashbalance(date)
                date += datetime.timedelta(days=1)
        elif action == 'delete':
            queryset = CashBalance.objects.filter(date__gte=from_date, date__lte=to_date).order_by('-date')
            for obj in queryset:
                start_time = datetime.datetime.now()
                obj.delete()
                end_time = datetime.datetime.now()
                delta = end_time-start_time
                print("Deleted cashbalance of",obj.date, "(Time:",delta.total_seconds(),")")

        return super().form_valid(form)
    