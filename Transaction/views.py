from django.shortcuts import render
from django.urls import reverse_lazy
import datetime
from django.views.generic.base import TemplateView
from django.db.models import Sum
from Product.models import Sell, Purchase
from Customer.models import DueSell, DueCollection
from Expenditure.models import Expenditure
from Revenue.models import Revenue
from .forms import DateForm

class DailyTransactionView(TemplateView):
    template_name = "Transaction/daily_transactions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = datetime.date.today().strftime("%Y-%m-%d")
        if 'date_day' in self.request.GET:
            date = datetime.date(int(self.request.GET.get('date_year')),
                int(self.request.GET.get('date_month')),
                int(self.request.GET.get('date_day')))
        else: date = datetime.date.today()
        date_str = date.strftime("%d/%m/%Y")
        # date_str = date.strftime("%d %B, %Y")
        # Queries
        sells = Sell.objects.filter(date=date)
        duecollections = DueCollection.objects.filter(date=date)
        revenues = Revenue.objects.filter(date=date)

        purchases = Purchase.objects.filter(date=date)
        duesells = DueSell.objects.filter(date=date)
        expenditures = Expenditure.objects.filter(date=date)

        context['date_form'] = DateForm(self.request.GET or None, initial={'date':today})
        context['date'] = date_str

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
        # Summary
        total_in = 0.0
        if context['total_sell']:
            total_in += context['total_sell']
        if context['total_duecollections']:
            total_in += context['total_duecollections']
        if context['total_revenues']:
            total_in += context['total_revenues']
        context['total_in'] = total_in

        total_out = 0.0
        if context['total_purchase']:
            total_out += context['total_purchase']
        if context['total_duesells']:
            total_out += context['total_duesells']
        if context['total_expenditures']:
            total_out += context['total_expenditures']
        context['total_out'] = total_out

        context['balance_cd'] = total_in - total_out
        return context
