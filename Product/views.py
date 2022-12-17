from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django import forms
from datetime import date

from .models import Product, SellingRate, Purchase, Sell
from .forms import SellForm, PurchaseForm

# Product
class ProductListView(ListView):
    model = Product

class ProductCreateView(CreateView):
    model = Product
    fields = '__all__'

class ProductUpdateView(UpdateView):
    model = Product
    fields = '__all__'

class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('product-list')

# Selling Rate
class SellingRateListView(ListView):
    model = SellingRate

class SellingRateCreateView(CreateView):
    model = SellingRate
    fields = ['product', 'start_date', 'start_time', 'rate']

    def get_form(self, form_class=None):
        form = super(SellingRateCreateView, self).get_form(form_class)
        form.fields['start_date'].widget = forms.SelectDateWidget()
        form.fields['start_time'].widget = forms.TimeInput(format='%H:%M:%S')
        return form

class SellingRateUpdateView(UpdateView):
    model = SellingRate
    fields = '__all__'

class SellingRateDeleteView(DeleteView):
    model = SellingRate
    success_url = reverse_lazy('selling-rates')

class SellListView(ListView):
    model = Sell

# Purchase
class PurchaseListView(ListView):
    model = Purchase

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = date.today()
        return context

class PurchaseCreateView(CreateView):
    model = Purchase
    form_class = PurchaseForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'date' in self.kwargs:
            context['form'].initial = {'date':self.kwargs['date']}
        return context

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

class SellUpdateView(UpdateView):
    model = Sell
    form_class = SellForm

class SellDeleteView(DeleteView):
    model = Sell
    
    def get_success_url(self):
        return reverse_lazy('daily-transactions', kwargs={'date':self.object.date})