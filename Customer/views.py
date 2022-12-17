from django.shortcuts import render
from django.urls import reverse_lazy
from datetime import date
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Customer, DueSell, DueCollection, GroupofCompany
from .forms import DueCollectionForm, DueSellForm

# Group of companies
class GroupofCompanyListView(ListView):
    model = GroupofCompany

class GroupofCompanyCreateView(CreateView):
    model = GroupofCompany
    fields = '__all__'

class GroupofCompanyUpdateView(UpdateView):
    model = GroupofCompany
    fields = '__all__'

class GroupofCompanyDeleteView(DeleteView):
    model = GroupofCompany
    success_url = reverse_lazy('groupofcompany-list')

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
    model = DueCollection

class DueCollectionCreateView(CreateView):
    model = DueCollection
    form_class = DueCollectionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'date' in self.kwargs:
            context['form'].initial = {'date':self.kwargs['date']}
        return context

class DueCollectionUpdateView(UpdateView):
    model = DueCollection
    form_class = DueCollectionForm

class DueCollectionDeleteView(DeleteView):
    model = DueCollection
    
    def get_success_url(self):
        return reverse_lazy('daily-transactions', kwargs={'date':self.object.date})

# Due Sell
class DueSellListView(ListView):
    model = DueSell

class DueSellCreateView(CreateView):
    model = DueSell
    form_class = DueSellForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'date' in self.kwargs:
            context['form'].initial = {'date':self.kwargs['date']}
        return context

class DueSellUpdateView(UpdateView):
    model = DueSell
    form_class = DueSellForm

class DueSellDeleteView(DeleteView):
    model = DueSell
    
    def get_success_url(self):
        return reverse_lazy('daily-transactions', kwargs={'date':self.object.date})