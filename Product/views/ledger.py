from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView, UpdateView

from Product.models import Product, Stock, InitialStock
from Product.views.purchase_sell import StockDeleteView
from Product.forms import InitialStockForm, ProductLedgerFilterForm
from Product.views.functions import monthly_product_category_details, daily_product_details
from Core.mixins import RedirectMixin, NavigationMixin
from Core.functions import account_start_date

class ProductTopSheet(NavigationMixin,TemplateView):
    template_name = 'Product/Ledger/product_topsheet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_category_details = monthly_product_category_details(self.from_date,self.date)
        context['product_category_details'] = product_category_details
        return context

class ProductLedger(NavigationMixin, TemplateView):
    template_name = 'Product/Ledger/product_ledger.html'

    def get(self,request,*args, **kwargs):
        if 'product' in self.request.GET:
            self.product = Product.objects.get(pk=self.request.GET.get('product'))
        elif 'product' in self.kwargs:
            self.product = Product.objects.get(pk=self.kwargs['product'])
        else: self.product = Product.objects.first()
        self.kwargs['product'] = self.product.pk
        return super().get(request,*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ProductLedgerFilterForm(
            initial={'date':self.date,'product':self.product}
        )
        context['product'] = self.product
        object_list, total = daily_product_details(self.from_date,self.date,self.product)
        context['object_list'] = object_list
        context['total'] = total
        return context

class InitialStockView(NavigationMixin, ListView):
    template_name = 'Product/Ledger/initial_stock.html'
    model = InitialStock
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_change'] = self.date == account_start_date()
        return context
    
    def get_queryset(self):
        return self.model.objects.filter(date=self.date)

class BaseInitialStockChangeView(InitialStockView):
    form_class = InitialStockForm

    def dispatch(self, request, *args, **kwargs):
        # First, call the parent dispatch method (which will call get())
        response = super().dispatch(request, *args, **kwargs)

        # Redirect logic after the mixin's get() is processed
        if self.date != account_start_date():
            return redirect(reverse('initial-stock', kwargs={'date': self.date}))
        
        # Return the response (whether it's a redirect or the regular get response)
        return response

class InitialStockCreateView(CreateView,BaseInitialStockChangeView): pass
class InitialStockUpdateView(UpdateView,BaseInitialStockChangeView): pass

class InitialStockDeleteView(StockDeleteView):
    model = InitialStock
    
    def get_success_url(self):
        return reverse('initial-stock',kwargs={'date':self.kwargs['date']})

class StockListView(RedirectMixin, ListView):
    model = Stock
    paginate_by = 20
    template_name = "Product/Ledger/stock_list.html"

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(pk=self.kwargs['product_id'])
        return context

    def get_queryset(self):
        return self.model.objects.filter(product=self.kwargs['product_id'])

class StockDetailsView(RedirectMixin, TemplateView):
    template_name = 'Product/Ledger/stock_details.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        if 'pk' in kwargs:
            stock = Stock.objects.get(pk=kwargs['pk'])
        else: raise ValueError("Error! Stock not mentioned.")
        context['stock'] = stock
        return context
        