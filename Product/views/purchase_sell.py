from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.views.generic import ListView
from Core.mixins import RedirectMixin
from Product.models import ConsumeStock
from django.db.models import Sum
from django.urls import reverse_lazy

from Transaction.functions import last_balance_date
from Core.mixins import RedirectMixin
from Product.models import Purchase, Sell
from Product.forms import SellForm, PurchaseForm    

class StockDeleteView(RedirectMixin, DeleteView):
    """
    Custom DeleteView that prevents deletion of objects if they have associated consumed stock.
    """
    template_name = 'delete.html'

    def get(self, request, *args, **kwargs):
        self.check_stock_consumption()
        self.delete(request, *args, **kwargs)
        return redirect(self.get_success_url())
        # try:
        #     # Run the consumption check before deletion
        # except ValidationError as e:
        #     # Handle the error by redirecting back and displaying a message
        #     messages.error(request, str(e))

    def check_stock_consumption(self):
        """
        Checks if any stock related to the instance has been consumed.
        """
        # Assuming the model has a 'stock' or similar relationship to Stock model
        stock_related = self.get_object().stock_set.all()
        for stock in stock_related:
            # If any consumption exists for the stock, raise an error
            if ConsumeStock.objects.filter(stock=stock).exists():
                raise ValidationError("This stock has been consumed and cannot be deleted.")

    def get_success_url(self):
        # Define the URL to redirect to upon successful deletion
        return self.success_url or '/'

# Purchase
class BasePurchaseSellView(RedirectMixin, ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = self.kwargs['date']
        qs = self.get_queryset()
        context['total'] = qs.aggregate(Sum('price'))['price__sum'] if qs else 0
        return context
    
    def get_queryset(self):
        return self.model.objects.filter(date=self.kwargs['date'])

class PurchaseCreateView(CreateView, BasePurchaseSellView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'Product/purchase.html'

class PurchaseUpdateView(UpdateView, BasePurchaseSellView):
    model = Purchase
    form_class = PurchaseForm
    template_name = 'Product/purchase.html'

class PurchaseDeleteView(StockDeleteView):
    model = Purchase

    def get_success_url(self):
        return reverse_lazy('create-purchase', kwargs={'date':self.kwargs['date']})

class SellCreateView(CreateView, BasePurchaseSellView):
    model = Sell
    form_class = SellForm
    template_name = 'Product/sell.html'

class SellUpdateView(UpdateView, BasePurchaseSellView):
    model = Sell
    form_class = SellForm
    template_name = 'Product/sell.html'

class SellDeleteView(DeleteView):
    model = Sell

    def get(self, request, *args, **kwargs):
        self.delete(request)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('create-sell', kwargs={'date':self.kwargs['date']})