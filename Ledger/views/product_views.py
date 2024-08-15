from django.shortcuts import redirect, render
from django.forms import modelformset_factory
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView
from django.db.models import Sum
from django.contrib import messages
from django.urls import reverse_lazy
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin

from Product.models import Product, StorageReading, Purchase, Sell
from Ledger.models import Storage
from Transaction.models import CashBalance
from Ledger.forms import StorageFilterForm, DateFilterForm, StorageUpdateForm
from Core.choices import all_dates_in_month, last_day_of_month
from Ledger.functions import get_products_info
from Transaction.functions import first_balance_date

class ProductTopSheet(LoginRequiredMixin,TemplateView):
    template_name = 'Ledger/product_topsheet.html'

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
        # For very first time
        if last_bal_date.year == first_bal_date.year and last_bal_date.month == first_bal_date.month:
            target_date = last_bal_date
        # Dont let go future
        if target_date > last_bal_date:
            return redirect('product-topsheet', month=last_bal_date.month, year=last_bal_date.year)
        elif target_date <= first_bal_date:
            return redirect('product-topsheet', month=first_date.month, year=first_date.year)

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
        product_data = []
        month = int(self.kwargs['month'])
        year = int(self.kwargs['year'])
        prev_month = self.kwargs['prev_month']
        prev_month_year = self.kwargs['prev_month_year']
        from_date = datetime.date(year,month,1)
        to_date = CashBalance.objects.filter(date__month=month,date__year=year).order_by('date').last().date
        last_day = last_day_of_month(year,month)
        context['status'] = last_day == to_date
        context['to_date'] = to_date
        product_data, total_profit, profit_adj = get_products_info(year,month)
        context['products'] = product_data
        total_ending_storage_amount = sum(product['ending_storage_amount'] for product in product_data)
        total_ending_storage_diff_amount = sum(product['ending_storage_diff_amount'] for product in product_data)
        context['total'] = {
            'ending_storage_amount': total_ending_storage_amount,
            'diff_amount': total_ending_storage_diff_amount,
            'actual_price': total_ending_storage_amount + total_ending_storage_diff_amount,
            'total_profit': total_profit
        }
        return context

class ProductLedger(LoginRequiredMixin,TemplateView):
    template_name = 'Ledger/product.html'

    def get(self, request, *args, **kwargs):
        if not CashBalance.objects.exists():
            return redirect('create-cashbalance')
        
        today = datetime.date.today()
        # pk
        if 'product' in self.request.GET:
            self.kwargs['pk'] = self.request.GET.get('product')
        elif 'pk' not in self.kwargs:
            self.kwargs['pk'] = Product.objects.first().pk
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
        target_date = datetime.date(year,month,1)
        self.kwargs['target_date'] = target_date

        storages = Storage.objects.filter(product=pk).order_by('year','month')
        if storages.count() == 0:
            context = self.get_context_data()
            return super(TemplateView, self).render_to_response(context)
        
        last_storage = storages.last()
        first_storage = storages.first()

        first_storage_date = datetime.date(int(first_storage.year),int(first_storage.month),1)
        last_storage_date = datetime.date(int(last_storage.year),int(last_storage.month),1)
        next_to_first = first_storage_date + datetime.timedelta(days=31)
        next_to_last = last_storage_date + datetime.timedelta(days=31)
        # print(next_to_first, next_to_last)
        
        if target_date > next_to_last:
            return redirect('product-ledger', 
                pk = self.kwargs['pk'], 
                month = next_to_last.month, 
                year = next_to_last.year)
        elif target_date < next_to_first:
            return redirect('product-ledger', 
                pk = self.kwargs['pk'], 
                month = next_to_first.month, 
                year = next_to_first.year)
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        pk = self.kwargs['pk']
        self.kwargs['product'] = pk
        month = self.kwargs['month']
        year = self.kwargs['year']
        target_date = self.kwargs['target_date']
        prev_date = target_date - datetime.timedelta(days=1)
        next_date = target_date + datetime.timedelta(days=31)
        context['prev'] = prev_date
        context['next'] = next_date

        product = Product.objects.get(pk=pk)
        purchase_rate = product.purchase_rate
        context['product'] = product

        context['filter_form'] = StorageFilterForm(self.request.GET or self.kwargs or None)
        context['month'] = month
        context['year'] = year

        data = []
        total_purchase_quantity = 0
        total_purchase_amount = 0
        total_sell_quantity = 0
        total_sell_amount = 0
        
        pre_storages = Storage.objects.filter(month=context['prev'].month,year=context['prev'].year,product=pk)
        # Loop every day in current month
        days = all_dates_in_month(year,month)
        diff_qnt_today = 0
        for day in days:
            # 1. তারিখ
            todays_data = {'date': day}
            # 2. প্রারম্ভিক মজুদ
            pre_storage_qnt = 0
            pre_storage_price = 0

            pre_sells = Sell.objects.filter(product=pk, date__gte=target_date, date__lt=day)
            pre_purchase = Purchase.objects.filter(product=pk, date__gte=target_date, date__lt=day)
            if pre_storages:
                pre_storage_qnt += pre_storages.last().quantity
                pre_storage_price += pre_storages.last().price
                # purchase_rate = pre_storage_price/pre_storage_qnt
            if pre_sells:
                pre_storage_qnt -= pre_sells.aggregate(Sum('quantity'))['quantity__sum']
                pre_storage_price -= pre_sells.aggregate(Sum('amount'))['amount__sum']
            if pre_purchase:
                pre_storage_qnt += pre_purchase.aggregate(Sum('quantity'))['quantity__sum']
                pre_storage_price += pre_purchase.aggregate(Sum('amount'))['amount__sum']
            # --------------------------------------
            todays_data['pre_storage_qnt'] = pre_storage_qnt
            todays_data['pre_storage_price'] = pre_storage_price
            # 3. ক্রয়
            purchase_qnt = 0
            purchase_amount = 0
            purchases = Purchase.objects.filter(date=day, product=pk)
            if purchases:
                purchase_qnt = purchases.aggregate(Sum('quantity'))['quantity__sum']
                todays_data['purchase_qnt'] = purchase_qnt
                total_purchase_quantity += purchase_qnt

                purchase_amount = purchases.aggregate(Sum('amount'))['amount__sum']
                todays_data['purchase_amount'] = purchase_amount
                total_purchase_amount += purchase_amount

                todays_data['purchase_rate'] = purchase_amount/purchase_qnt if purchase_qnt else 0
            # 4. বিক্রয়
            sell_qnt = 0
            sell_amount = 0
            sells = Sell.objects.filter(date=day, product=pk)
            if sells:
                sell_qnt = sells.aggregate(Sum('quantity'))['quantity__sum']
                sell_amount = sells.aggregate(Sum('amount'))['amount__sum']
            todays_data['sell_qnt'] = sell_qnt
            todays_data['sell_amount'] = sell_amount
            todays_data['selling_rate'] = sell_amount/sell_qnt if sell_qnt > 0 else 0
            total_sell_quantity += sell_qnt
            total_sell_amount += sell_amount
            # 5. অবশিষ্ট মজুদ
            remaining_storage = pre_storage_qnt + purchase_qnt - sell_qnt
            todays_data['remaining_storage_qnt'] = remaining_storage
            todays_data['remaining_storage_amount'] = remaining_storage * purchase_rate
            # 6-7. ট্যাংক ডিপ + লোড
            tank_deep = 0
            lorry_load = 0
            storage_qnt = 0
            storage_amount = 0
            storage_readings = StorageReading.objects.filter(date=day, product=pk)
            if storage_readings:
                storage_reading = storage_readings.last()
                tank_deep = storage_reading.tank_deep
                lorry_load = storage_reading.lorry_load
            todays_data['tank_deep'] = tank_deep
            todays_data['lorry_load'] = lorry_load
            storage_qnt = tank_deep + lorry_load
            todays_data['storage_qnt'] = storage_qnt
            storage_amount = product.purchase_rate * storage_qnt
            todays_data['storage_amount'] = storage_amount
            # 8. ব্যবধান
            diff_qnt = storage_qnt - remaining_storage

            todays_data['diff_qnt_today'] = diff_qnt - diff_qnt_today
            diff_qnt_today = diff_qnt

            todays_data['diff_qnt'] = diff_qnt
            todays_data['diff_amount'] = diff_qnt * purchase_rate
            if sell_qnt != 0 or purchase_qnt != 0:
                data.append(todays_data)
        context['qs'] = data
        context['total'] = {
            'total_purchase_quantity': total_purchase_quantity,
            'total_purchase_amount': total_purchase_amount,
            'purchase_rate': total_purchase_amount/total_purchase_quantity if total_purchase_quantity else 0,
            'total_sell_quantity': total_sell_quantity,
            'total_sell_amount': total_sell_amount,
            'selling_rate': total_sell_amount/total_sell_quantity if total_sell_quantity else 0,
        }
        return context

# To store balances/Storage
class StorageView(LoginRequiredMixin, ListView):
    model = Storage
    template_name = 'Ledger/storage.html'

    def get(self,request,*args, **kwargs):
        today = datetime.date.today()
        if 'month' not in self.kwargs and 'year' not in self.kwargs:
            if Storage.objects.exists():
                # first_bal_date = Storage.objects.first().date
                last_bal_date = Storage.objects.order_by('year','month').last()
                self.kwargs['month'] = last_bal_date.month
                self.kwargs['year'] = last_bal_date.year
            # elif 'month' in self.request.GET and 'year' in self.request.GET:
            #     self.kwargs['month'] = int(self.request.GET['month'])
            #     self.kwargs['year'] = int(self.request.GET['year'])
            else:
                self.kwargs['month'] = today.month
                self.kwargs['year'] = today.year

        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        month = self.kwargs['month']
        year = self.kwargs['year']
        qs = self.model.objects.filter(month=month, year=year)
        return qs
      
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
        context['storage_month'] = month
        context['storage_year'] = year
        qs = self.get_queryset()
        if qs:
            context['total'] = qs.aggregate(Sum('price'))['price__sum']
        return context

def storage_formset_view(request,month,year):
    first_date = first_balance_date()
    empty_storages = Storage.objects.filter(quantity=0, month=first_date.month, year=first_date.year)
    print(first_date.month, first_date.year, empty_storages)
    
    storage_formset_factory = modelformset_factory(Storage, StorageUpdateForm, extra=0)
    storage_formset = storage_formset_factory(request.POST or None, queryset=empty_storages, prefix='storage')
    storage_formset.initial = [{'product':obj.product} for obj in empty_storages]

    template = "Ledger/storage_formset.html"
    context = {
        'formset': storage_formset,
        'month': month, 'year':year
        }

    return render(request,template,context)