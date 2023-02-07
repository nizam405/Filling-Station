from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView
from django.db.models import Sum
from django.contrib import messages
from django.urls import reverse_lazy
import datetime

from Product.models import Product, StorageReading, Purchase, Sell
from Ledger.models import Storage
from Ledger.forms import StorageFilterForm
from Core.choices import all_dates_in_month

# To store balances/Storage
class StorageView(CreateView, ListView):
    model = Storage
    fields = ['month','year','product','quantity']
    template_name = 'Ledger/storage.html'

    def get(self,request,*args, **kwargs):
        today = datetime.date.today()
        if Storage.objects.exists():
            # first_bal_date = Storage.objects.first().date
            last_bal_date = Storage.objects.last()
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
        return reverse_lazy('product-storage', kwargs=self.kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        month = form.cleaned_data['month']
        year = form.cleaned_data['year']
        return redirect(reverse_lazy('product-storage', kwargs={'month':month, 'year':year}))
    
    def form_invalid(self, form):
        self.object_list = self.get_queryset()
        messages.error(self.request, "মজুদ মাল মাসে একবারই লিপিবদ্ধ হয়!")
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
        context['storage_month'] = month
        context['storage_year'] = year
        qs = self.get_queryset()
        if qs:
            context['total'] = qs.aggregate(Sum('price'))['price__sum']
        return context

class ProductLedger(TemplateView):
    template_name = 'Ledger/product.html'

    def get(self, request, *args, **kwargs):
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

        storages = Storage.objects.filter(product=pk)
        if storages.count() == 0:
            context = self.get_context_data()
            return super(TemplateView, self).render_to_response(context)
        
        last_storage = storages.last()
        first_storage = storages.first()

        target_date = datetime.date(year,month,1)
        first_storage_date = datetime.date(int(first_storage.year),int(first_storage.month),1)
        last_storage_date = datetime.date(int(last_storage.year),int(last_storage.month),1)
        next_to_first = first_storage_date + datetime.timedelta(days=31)
        next_to_last = last_storage_date + datetime.timedelta(days=31)
        
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
        target_date = datetime.date(year,month,1) # মাসের প্রথম তারিখ

        product = Product.objects.get(pk=pk)
        context['product'] = product

        context['filter_form'] = StorageFilterForm(self.request.GET or self.kwargs or None)
        context['month'] = month
        context['year'] = year
        # prev and next month
        context['prev'] = {
            'month': month - 1 if month > 1 else 12,
            'year': year if month > 1 else year - 1
        }
        context['next'] = {
            'month': month + 1 if month < 12 else 1,
            'year': year  if month < 12 else year + 1
        }

        data = []
        total_purchase_quantity = 0
        total_purchase_amount = 0
        total_sell_quantity = 0
        total_sell_amount = 0
        
        pre_storages = Storage.objects.filter(month=context['prev']['month'],product=pk)
        # Loop every day in current month
        days = all_dates_in_month(year,month)
        for day in days:
            # 1. তারিখ
            todays_data = {'date': day}
            # 2. প্রারম্ভিক মজুদ
            pre_storage_qnt = 0
            pre_storage_price = 0

            # প্রতিদিনের ট্যাংক ডিপ ও লরি লোড কে পরবর্তী দিন প্রারম্ভিক মজুল হিসেব করলেঃ
            # ডিজেল, অকটেন need_rescale=True, মাসের প্রথম তারিখ না হলে, গত দিনের মজুদ আসবে
            # if product.need_rescale and day != target_date:
            #     pre_storages = StorageReading.objects.filter(date=day-datetime.timedelta(days=1), product=pk)
            #     if pre_storages:
            #         pre_storage = pre_storages.last()
            #         pre_storage_qnt = pre_storage.tank_deep + pre_storage.lorry_load
            # else:
            #     # বাকি সকল মালের জন্য পুর্ববর্তী মাসের মজুদ আসবে
            #     # ডিজেল, অকটেন এর প্রথম দিনের প্রারম্ভিক মজুদ
            #     pre_storages = Storage.objects.filter(month=context['prev']['month'],product=pk)
            #     if pre_storages:
            #         pre_storage = pre_storages.last()
            #         pre_storage_qnt = pre_storage.amount + total_purchase_quantity - total_sell_quantity
            # pre_storage_price = int(product.purchase_rate * pre_storage_qnt)
            # --------------------------------------
           
            # গতমাসের ব্যাল্যান্স এর সাথে গতকাল পর্যন্ত হিসেব করে
            # prev_date = day - datetime.timedelta(days=1)
            pre_sells = Sell.objects.filter(product=pk, date__gte=target_date, date__lt=day)
            # print(pre_sells)
            pre_purchase = Purchase.objects.filter(product=pk, date__gte=target_date, date__lt=day)
            # print(pre_purchase)
            if pre_storages:
                pre_storage_qnt += pre_storages.last().quantity
            if pre_sells:
                pre_storage_qnt -= pre_sells.aggregate(Sum('quantity'))['quantity__sum']
            if pre_purchase:
                pre_storage_qnt += pre_purchase.aggregate(Sum('quantity'))['quantity__sum']
            
            pre_storage_price = int(product.purchase_rate * pre_storage_qnt)
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
            # 4. বিক্রয়
            # duesells = DueSell.objects.filter(date=day, product=pk)
            sell_qnt = 0
            sell_amount = 0
            # if duesells:
            #     sell_qnt += duesells.aggregate(Sum('quantity'))['quantity__sum']
            #     sell_amount += duesells.aggregate(Sum('amount'))['amount__sum']
            sells = Sell.objects.filter(date=day, product=pk)
            if sells:
                sell_qnt = sells.aggregate(Sum('quantity'))['quantity__sum']
                sell_amount = sells.aggregate(Sum('amount'))['amount__sum']
            todays_data['sell_qnt'] = sell_qnt
            todays_data['sell_amount'] = sell_amount
            total_sell_quantity += sell_qnt
            total_sell_amount += sell_amount
            # 5. অবশিষ্ট মজুদ
            todays_data['remaining_storage_qnt'] = pre_storage_qnt + purchase_qnt - sell_qnt
            todays_data['remaining_storage_amount'] = pre_storage_price + purchase_amount - sell_amount
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
            storage_amount = int(product.purchase_rate * storage_qnt)
            todays_data['storage_amount'] = storage_amount
            # 8. ব্যবধান
            diff_qnt = storage_qnt - todays_data['remaining_storage_qnt']
            todays_data['diff_qnt'] = diff_qnt
            todays_data['diff_amount'] = int(diff_qnt * product.purchase_rate)
            if sell_qnt != 0 or purchase_qnt != 0:
                data.append(todays_data)
        context['qs'] = data
        context['total'] = {
            'total_purchase_quantity': total_purchase_quantity,
            'total_purchase_amount': total_purchase_amount,
            'total_sell_quantity': total_sell_quantity,
            'total_sell_amount': total_sell_amount,
        }
        return context

