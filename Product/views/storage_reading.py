from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from Core.mixins import RedirectMixin
from Product.models import StorageReading, Excess, Shortage, Stock
from Product.forms import StorageReadingForm
from Transaction.functions import last_balance_date

# Storage Reading
class BaseStorageReadingView(RedirectMixin, ListView):
    model = StorageReading
    template_name = 'Product/storage_reading.html'
    form_class = StorageReadingForm
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'date' in self.kwargs:
            context["date"] = self.kwargs['date']
            context['last_bal_date'] = last_balance_date()
        return context
    
    def get_queryset(self):
        qs = super().get_queryset()
        if 'date' in self.kwargs:
            qs = qs.filter(date=self.kwargs['date'])
        return qs

class StorageReadingView(CreateView, BaseStorageReadingView):
    def get_success_url(self):
        url = reverse_lazy('daily-product-storage')
        if 'date' in self.kwargs:
            url = reverse_lazy('daily-product-storage', kwargs={'date':self.kwargs['date']})
        return  url

    def get_initial(self):
        initial = super().get_initial()
        if 'date' in self.kwargs:
            date = self.kwargs['date']
            initial.update({'date':date})
        return initial

class StorageReadingUpdateView(UpdateView, BaseStorageReadingView):
    def get_queryset(self):
        if 'date' in self.kwargs:
            date = self.kwargs['date']
            queryset = self.model.objects.filter(date=date)
            return queryset
        return super().get_queryset()

class StorageReadingDeleteView(RedirectMixin,  DeleteView):
    model = StorageReading
    success_url = reverse_lazy('daily-product-storage')

# Excess/Shortage
class StockAdjustment(RedirectMixin, TemplateView):
    
    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        return context

class BaseExcessEditView(RedirectMixin):
    model = Excess
    fields = '__all__'

class ExcessCreateView(CreateView, BaseExcessEditView): pass
class ExcessUpdateView(UpdateView, BaseExcessEditView): pass

class BaseShortageEditView(RedirectMixin): 
    model = Shortage
    fields = ['date','stock','quantity']
    template_name = 'Product/shortage.html'

    def get_initial(self):
        initial = super().get_initial()
        stock = Stock.objects.get(pk=self.kwargs['stock'])
        initial['stock'] = stock
        return initial
    
    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['stock'] = Stock.objects.get(pk=self.kwargs['stock'])
        return context

class ShortageCreateView(BaseShortageEditView, CreateView): pass
class ShortageUpdateView(BaseShortageEditView, UpdateView): pass

class ShortageDeleteView(DeleteView):
    model = Shortage

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        object.delete()
        return redirect('stock-details',pk=object.stock.pk)
