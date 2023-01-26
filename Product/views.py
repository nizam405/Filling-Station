from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .models import Product, Purchase, Sell, StorageReading
from .forms import SellForm, PurchaseForm, StorageReadingForm

# Product
class ProductView(CreateView, ListView):
    model = Product
    fields = '__all__'
    template_name = 'Product/products.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        return context

class ProductUpdateView(UpdateView, ListView):
    model = Product
    fields = '__all__'
    template_name = 'Product/products.html'
    success_url = reverse_lazy('products')

class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('products')

# Storage Reading
class StorageReadingView(CreateView, ListView):
    model = StorageReading
    template_name = 'Product/storage.html'
    success_url = '.'
    fields = '__all__'
    
    def get_queryset(self):
        if 'date' in self.kwargs:
            date = self.kwargs['date']
            queryset = self.model.objects.filter(date=date)
            return queryset
        return super().get_queryset()

    def get_initial(self):
        initial = super().get_initial()
        if 'date' in self.kwargs:
            initial.update({'date':self.kwargs['date']})
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'date' in self.kwargs:
            context["date"] = self.kwargs['date']
        return context
    

class StorageReadingtUpdateView(UpdateView, ListView):
    model = StorageReading
    template_name = 'Product/storage.html'
    success_url = reverse_lazy('daily-product-storage')
    fields = '__all__'
    
    def get_queryset(self):
        if 'date' in self.kwargs:
            date = self.kwargs['date']
            queryset = self.model.objects.filter(date=date)
            return queryset
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'date' in self.kwargs:
            context["date"] = self.kwargs['date']
        return context

class StorageReadingDeleteView(DeleteView):
    model = StorageReading
    success_url = reverse_lazy('daily-product-storage')

# Purchase
def PurchaseFormsetView(request, date):
    qs = Purchase.objects.filter(date=date)
    extra = 0 if qs.count() > 0 else 1
    PurchaseFormSet = modelformset_factory(Purchase, form=PurchaseForm, extra=extra, can_delete=True)
    formset = PurchaseFormSet(request.POST or None, queryset=qs)
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Product/purchase_formset.html"
    context = {
        'formset': formset, 
        'empty_form': empty_form,
        'date': date,
        }

    if request.method == 'POST':
        if formset.errors:
            print(formset.errors)
        if formset.is_valid():
            formset.save()
            return redirect('daily-transactions', date)
    return render(request,template,context)

# Sell
def SellFormsetView(request, date):
    qs = Sell.objects.filter(date=date)
    extra = 0 if qs.count() > 0 else 1
    SellFormSet = modelformset_factory(Sell, SellForm, extra=extra, can_delete=True)
    formset = SellFormSet(request.POST or None, queryset=qs)
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Product/sell_formset.html"
    context = {
        'formset': formset, 
        'empty_form': empty_form,
        'date': date,
        }

    if request.method == 'POST':
        if formset.errors:
            print(formset.errors)
        if formset.is_valid():
            formset.save()
            return redirect('daily-transactions', date)
    return render(request,template,context)