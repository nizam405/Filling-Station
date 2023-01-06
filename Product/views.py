from django.shortcuts import render, redirect
from django.forms import formset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from datetime import date

from .models import Product, Purchase, Sell
from .forms import SellForm, PurchaseForm

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

# Purchase
class PurchaseListView(ListView):
    model = Purchase

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = date.today()
        return context

# class PurchaseCreateView(CreateView):
#     model = Purchase
#     form_class = PurchaseForm

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if 'date' in self.kwargs:
#             context['form'].initial = {'date':self.kwargs['date']}
#         return context

def MultiPurchaseCreateView(request, date):
    PurchaseFormSet = formset_factory(PurchaseForm, extra=0)
    formset = PurchaseFormSet(request.POST or None, initial=[{'date':date}])
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Product/purchase_formset.html"
    context = {
        'formset': formset, 
        'empty_form': empty_form,
        'date': date,
        'products': Product.objects.all()
        }

    if request.method == 'POST':
        if formset.errors:
            print(formset.errors)
        if formset.is_valid():
            for form in formset:
                form.save()
            return redirect('daily-transactions', date)
    return render(request,template,context)

class PurchaseUpdateView(UpdateView):
    model = Purchase
    form_class = PurchaseForm

class PurchaseDeleteView(DeleteView):
    model = Purchase
    
    def get_success_url(self):
        return reverse_lazy('daily-transactions', kwargs={'date':self.object.date})

# Sell
class SellListView(ListView):
    model = Sell

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = date.today()
        return context

class SellCreateView(CreateView):
    model = Sell
    form_class = SellForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'date' in self.kwargs:
            context['form'].initial = {'date':self.kwargs['date']}
        return context

def MultiSellCreateView(request, date):
    SellFormSet = formset_factory(SellForm, extra=0)
    formset = SellFormSet(request.POST or None, initial=[{'date':date}])
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Product/sell_formset.html"
    context = {
        'formset': formset, 
        'empty_form': empty_form,
        'date': date,
        'products': Product.objects.all()
        }

    if request.method == 'POST':
        if formset.errors:
            print(formset.errors)
        if formset.is_valid():
            for form in formset:
                form.save()
            return redirect('daily-transactions', date)
    return render(request,template,context)

class SellUpdateView(UpdateView):
    model = Sell
    form_class = SellForm

class SellDeleteView(DeleteView):
    model = Sell
    
    def get_success_url(self):
        return reverse_lazy('daily-transactions', kwargs={'date':self.object.date})