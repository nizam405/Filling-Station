from django.shortcuts import redirect
from django.urls import reverse_lazy
import datetime
from django.views.generic.base import TemplateView, View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.db.models import Sum
from django.conf import settings

from Product.models import Sell, Purchase, StorageReading
from Customer.models import DueSell, DueCollection, Customer
from IncomeExpenditure.models import Income, Expenditure, IncomeGroup, ExpenditureGroup
from Owner.models import Withdraw, Investment
from Product.models import Product
from Loan.models import BorrowLoan, LendLoan, RefundLendedLoan, RefundBorrowedLoan
from .forms import CashBalanceForm, CashBalanceForm2, CashBalanceControlForm
from .models import CashBalance
from .functions import save_cashbalance, last_balance_date, next_to_last_balance_date
from Core.mixins import NavigationMixin, RedirectMixin
from Core.functions import next_day
from Product.choices import FUEL

class DailyTransactionView(NavigationMixin, TemplateView):
    template_name = "Transaction/daily_transactions.html"

    def post(self, request, **kwargs):
        form = CashBalanceForm2(self.request.POST)

        if form.is_valid():
            self.date = last_balance_date()
            next_date = next_to_last_balance_date()
            amount = form.cleaned_data.get('amount')
            balance_cf = form.cleaned_data.get('balance_cf')
            diff = amount - balance_cf
            print(next_date,self.date,diff)
            if balance_cf < amount: 
                group, created = IncomeGroup.objects.get_or_create(name='বিবিধ')
                obj = Income.objects.create(
                    group = group,
                    date = self.date,
                    detail = 'ক্যাশ বাক্সে উদ্ধ্বৃত',
                    amount = diff
                )
            elif balance_cf > amount: 
                group, created = ExpenditureGroup.objects.get_or_create(name='বিবিধ')
                obj = Expenditure.objects.create(
                    group = group,
                    date = self.date,
                    detail = 'ক্যাশ বাক্সে ঘাটতি',
                    amount = abs(diff)
                )
            # form.save()
            CashBalance.objects.create(date=next_date,amount=amount)
        else: print(form.errors)
        # save_cashbalance(next_day(self.date))
        return redirect('.')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Queries
        sells = Sell.objects.filter(date=self.date)
        duecollections = DueCollection.objects.filter(date=self.date).order_by('id')
        incomes = Income.objects.filter(date=self.date)
        investments = Investment.objects.filter(date=self.date)
        # হাওলাদ গ্রহণ
        borrowed_loans = BorrowLoan.objects.filter(date=self.date)
        # প্রদত্ত হাওলাদ ফেরত
        refund_lended_loans = RefundLendedLoan.objects.filter(date=self.date)

        purchases = Purchase.objects.filter(date=self.date)
        # Duesell
        duesells = DueSell.objects.filter(date=self.date)
        customers = Customer.objects.all()
        duesell_data = []
        for customer in customers:
            cust_duesells = duesells.filter(customer=customer)
            if cust_duesells.exists():
                duesell_data.append({
                    'customer': customer,
                    'due_sells': cust_duesells,
                    'cust_total': cust_duesells.aggregate(Sum('price'))['price__sum']
                })

        expenditures = Expenditure.objects.filter(date=self.date)
        withdraws = Withdraw.objects.filter(date=self.date)
        
        # হাওলাদ প্রদান
        lended_loans = LendLoan.objects.filter(date=self.date)
        # গৃহীত হাওলাদ পরিশোধ
        refund_borrowed_loans = RefundBorrowedLoan.objects.filter(date=self.date)

        context['sells'] = sells
        context['total_sell'] = sells.aggregate(Sum('price'))['price__sum'] or 0
        context['duesells'] = duesell_data
        context['total_duesell'] = duesells.aggregate(Sum('price'))['price__sum'] or 0
        context['cash_sell'] = context['total_sell'] - context['total_duesell']
        context['duecollections'] = duecollections
        context['total_duecollection'] = duecollections.aggregate(Sum('amount'))['amount__sum']
        context['incomes'] = incomes
        context['total_income'] = incomes.aggregate(Sum('amount'))['amount__sum']
        context['investments'] = investments
        context['total_investments'] = investments.aggregate(Sum('amount'))['amount__sum']
        context['borrowed_loans'] = borrowed_loans
        context['total_borrowed_loan'] = borrowed_loans.aggregate(Sum('amount'))['amount__sum']
        context['refund_lended_loans'] = refund_lended_loans
        context['total_refund_lended_loan'] = refund_lended_loans.aggregate(Sum('amount'))['amount__sum']

        context['purchases'] = purchases
        context['total_purchase'] = purchases.aggregate(Sum('price'))['price__sum']
        context['expenditures'] = expenditures
        context['total_expenditure'] = expenditures.aggregate(Sum('amount'))['amount__sum']
        context['withdraws'] = withdraws
        context['total_withdraw'] = withdraws.aggregate(Sum('amount'))['amount__sum']
        context['lended_loans'] = lended_loans
        context['total_lended_loan'] = lended_loans.aggregate(Sum('amount'))['amount__sum']
        context['refund_borrowed_loans'] = refund_borrowed_loans
        context['total_refund_borrowed_loan'] = refund_borrowed_loans.aggregate(Sum('amount'))['amount__sum']
        
        # Balance B/F
        balance_bf = CashBalance.objects.get(date=self.date)
        context['balance_bf'] = balance_bf.amount
        
        # Balance C/F
        total_debit = 0
        total_credit = 0
        if balance_bf.amount > 0:
            total_debit += balance_bf.amount
        else: total_credit += balance_bf.amount
        
        total_debit += context['cash_sell']
        if context['total_duecollection']: total_debit += context['total_duecollection']
        if context['total_income']: total_debit += context['total_income']
        if investments: total_debit += context['total_investments']
        if borrowed_loans: total_debit += context['total_borrowed_loan']
        if refund_lended_loans: total_debit += context['total_refund_lended_loan']
        context['total_debit'] = total_debit

        if context['total_purchase']: total_credit += context['total_purchase']
        # if context['total_duesell']: total_credit += context['total_duesell']
        if context['total_expenditure']: total_credit += context['total_expenditure']
        if context['total_withdraw']: total_credit += context['total_withdraw']
        if lended_loans: total_credit += context['total_lended_loan']
        if refund_borrowed_loans: total_credit += context['total_refund_borrowed_loan']
        context['total_credit'] = total_credit
        balance_cf = total_debit - total_credit
        context['balance_cf'] = balance_cf
        context['total_credit'] += balance_cf

        saved_balance = CashBalance.objects.filter(date=next_day(self.date))
        if saved_balance:
            context['saved_balance_cf'] = saved_balance.last().amount
            context['can_change'] = False
        else: 
            context['can_change'] = True
            next_date = next_day(self.date).strftime(settings.DATE_FORMAT)
            context['balance_form'] = CashBalanceForm2(
                initial={'amount': round(balance_cf),'balance_cf':balance_cf}
            )

        storage_readings = StorageReading.objects.filter(date=self.date)
        count_fuels = Product.objects.filter(category=FUEL).count()
        context['storage_readings'] = storage_readings
        context['has_fuels'] = bool(count_fuels)
        context['can_save'] = False
        context['pattern_name'] = 'daily-transactions'
        if count_fuels == storage_readings.count():
            context['can_save'] = True

        return context

class SaveDailyCashBalanceView(RedirectMixin,View):
    def get(self,request,*args, **kwargs):
        # save_cashbalance(self.date)
        date = self.kwargs['date']
        amount = float(self.kwargs['amount'])
        CashBalance.objects.create(date=date,amount=amount)
        return redirect('daily-transactions',date=date)

class CashBalanceListView(ListView):
    model = CashBalance
    ordering = ['-date']
    paginate_by = 30

class CashBalanceCreateView(CreateView):
    model = CashBalance
    form_class = CashBalanceForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'date' in self.kwargs:
            context['date'] = self.kwargs['date']
            context['form'].initial = {'date':context['date']}
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
    
class CashBalanceControlView(FormView):
    form_class = CashBalanceControlForm
    template_name = 'Transaction/cashbalance_control_form.html'
    success_url = reverse_lazy('daily-transactions')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        to_date = last_balance_date()
        from_date = last_balance_date()
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
    