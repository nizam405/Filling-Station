from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Product, Purchase, Sell, StorageReading
from .forms import SellForm, PurchaseForm, StorageReadingForm
from datetime import timedelta

# Product
class ProductView(LoginRequiredMixin,CreateView, ListView):
    model = Product
    fields = '__all__'
    template_name = 'Product/products.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        return context

def change_product_status(request, pk):
    product = Product.objects.get(pk=pk)
    product.active = not product.active
    product.save()
    return redirect('products')

class ProductUpdateView(LoginRequiredMixin,UpdateView, ListView):
    model = Product
    fields = '__all__'
    template_name = 'Product/products.html'
    success_url = reverse_lazy('products')

class ProductDeleteView(LoginRequiredMixin,DeleteView):
    model = Product
    success_url = reverse_lazy('products')

# Storage Reading
class StorageReadingView(LoginRequiredMixin,CreateView, ListView):
    model = StorageReading
    template_name = 'Product/storage.html'
    # fields = '__all__'
    form_class = StorageReadingForm
    paginate_by = 20

    def get_success_url(self):
        url = reverse_lazy('daily-product-storage')
        if 'date' in self.kwargs:
            url = reverse_lazy('daily-product-storage', kwargs={'date':self.kwargs['date']})
        return  url

    def get_initial(self):
        initial = super().get_initial()
        if self.model.objects.exists():
            date = self.model.objects.order_by('date').last().date
            qs = self.model.objects.filter(date=date)
            if qs.count() > 1:
                date = date + timedelta(days=1)
        elif 'date' in self.kwargs:
            date = self.kwargs['date']
        initial.update({'date':date})
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'date' in self.kwargs:
            context["date"] = self.kwargs['date']
        return context
    
class StorageReadingtUpdateView(LoginRequiredMixin,UpdateView, ListView):
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

class StorageReadingDeleteView(LoginRequiredMixin,DeleteView):
    model = StorageReading
    success_url = reverse_lazy('daily-product-storage')

# Purchase
@login_required
def PurchaseFormsetView(request, date):
    qs = Purchase.objects.filter(date=date)
    # No extra form for edit or delete
    extra = 0 if qs.count() > 0 else 1
    PurchaseFormSet = modelformset_factory(Purchase, form=PurchaseForm, extra=extra, can_delete=True)
    formset = PurchaseFormSet(request.POST or None, queryset=qs)
    formset.initial = [{'date':date} for i in range(0,extra)]
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
@login_required
def SellFormsetView(request, date):
    qs = Sell.objects.filter(date=date)
    extra = 0 if qs.count() > 0 else 1
    SellFormSet = modelformset_factory(Sell, SellForm, extra=extra, can_delete=True)
    formset = SellFormSet(request.POST or None, queryset=qs)
    formset.initial = [{'date':date} for i in range(0,extra)]
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