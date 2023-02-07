from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.db.models import Sum
from django.db.models import Value
from django.db.models.functions import Concat
import datetime
import calendar
from Customer.models import Customer, GroupofCompany, DueSell, DueCollection
from Product.models import Product, Purchase, Sell, StorageReading
from Expenditure.models import ExpenditureGroup, Expenditure
from Revenue.models import RevenueGroup, Revenue
from Owner.models import Withdraw, Owner
from Ledger.models import CustomerBalance, GroupofCompanyBalance, Storage
from Ledger.forms import DateFilterForm

class IncomeStatementView(TemplateView):
    template_name = 'Ledger/incomestatement.html'

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
        # here num_days+7 to make sure it goes to next month
        self.kwargs['next_date'] = target_date + datetime.timedelta(days=num_days+7)

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
        context.update(self.get_product_data())
        return context
    
    def get_product_data(self):
        context = {}
        month = int(self.kwargs['month'])
        year = int(self.kwargs['year'])
        prev_month = self.kwargs['prev_month']
        prev_month_year = self.kwargs['prev_month_year']

        sells = Sell.objects.filter(date__month=month,date__year=year)
        purchases = Purchase.objects.filter(date__month=month,date__year=year)
        pre_storages = Storage.objects.filter(month=prev_month, year=prev_month_year)

        sells_amount = 0
        if sells:
            sells_amount = sells.aggregate(Sum('amount'))['amount__sum']
        purchase_amount = 0
        if purchases:
            purchase_amount = purchases.aggregate(Sum('amount'))['amount__sum']
        context['sells'] = sells_amount
        context['purchases'] = purchase_amount


        return context