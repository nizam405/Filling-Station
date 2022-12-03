from django.shortcuts import render
from django.urls import reverse_lazy
import datetime
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Customer, DueSell, DueCollection
from .forms import DueCollectionForm, DueSellForm

# Customer
class CustomerListView(ListView):
    model = Customer

class CustomerDetailView(DetailView):
    model = Customer

class CustomerCreateView(CreateView):
    model = Customer
    fields = '__all__'

class CustomerUpdateView(UpdateView):
    model = Customer
    fields = '__all__'

class CustomerDeleteView(DeleteView):
    model = Customer
    success_url = reverse_lazy('customer-list')
    
# Due Collection
class DueCollectionListView(ListView):
    # template_name = 'Customer/duecollection_list.html'
    model = DueCollection

class DueCollectionCreateView(CreateView):
    # template_name = 'Customer/duecollection_form.html'
    model = DueCollection
    form_class = DueCollectionForm

class DueCollectionUpdateView(UpdateView):
    # template_name = 'Customer/duecollection_form.html'
    model = DueCollection
    form_class = DueCollectionForm

class DueCollectionDeleteView(DeleteView):
    # template_name = 'Customer/duecollection_confirm_delete.html'
    model = DueCollection
    success_url = reverse_lazy('duecollection-list')

# Due Sell
class DueSellListView(ListView):
    # template_name = 'Customer/duesell_list.html'
    model = DueSell

class DueSellCreateView(CreateView):
    # template_name = 'Customer/duesell_form.html'
    model = DueSell
    form_class = DueSellForm

class DueSellUpdateView(UpdateView):
    # template_name = 'Customer/duesell_form.html'
    model = DueSell
    form_class = DueSellForm

class DueSellDeleteView(DeleteView):
    # template_name = 'Customer/duesell_confirm_delete.html'
    model = DueSell
    success_url = reverse_lazy('duesell-list')