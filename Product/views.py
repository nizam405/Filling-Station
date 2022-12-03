from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django import forms

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

class PurchaseCreateView(CreateView):
    model = Purchase
    form_class = PurchaseForm

class PurchaseUpdateView(UpdateView):
    model = Purchase
    form_class = PurchaseForm

class PurchaseDeleteView(DeleteView):
    model = Purchase
    success_url = reverse_lazy('purchases')

# Sell
class SellListView(ListView):
    model = Sell

class SellCreateView(CreateView):
    model = Sell
    form_class = SellForm

class SellUpdateView(UpdateView):
    model = Sell
    form_class = SellForm

class SellDeleteView(DeleteView):
    model = Sell
    success_url = reverse_lazy('sells')