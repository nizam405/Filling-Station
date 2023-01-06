from django.shortcuts import render, redirect
from django.forms import formset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Customer, DueSell, DueCollection, GroupofCompany
from .forms import DueCollectionForm, DueSellForm, CustomerForm
from Product.models import Product

# Group of companies
class GroupofCompaniesView(CreateView, ListView):
    model = GroupofCompany
    fields = '__all__'
    template_name = 'Customer/groupofcompanies.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        return context

class GroupofCompanyUpdateView(UpdateView, ListView):
    model = GroupofCompany
    fields = '__all__'
    template_name = 'Customer/groupofcompanies.html'
    success_url = reverse_lazy('groupofcompanies')

class GroupofCompanyDeleteView(DeleteView):
    model = GroupofCompany
    success_url = reverse_lazy('groupofcompanies')

# Customer
class CustomerView(CreateView, ListView):
    model = Customer
    fields = '__all__'
    template_name = 'Customer/customers.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        return context

class CustomerUpdateView(UpdateView, ListView):
    model = Customer
    fields = '__all__'
    template_name = 'Customer/customers.html'
    success_url = reverse_lazy('customers')

class CustomerDeleteView(DeleteView):
    model = Customer
    success_url = reverse_lazy('customers')
    
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

def MultiDueCollectionCreateView(request, date):
    DueCollectionFormSet = formset_factory(DueCollectionForm, extra=0)
    formset = DueCollectionFormSet(request.POST or None, initial=[{'date':date}])
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Customer/duecollection_formset.html"
    context = {
        'formset': formset, 
        'empty_form': empty_form,
        'date': date,
        }

    if request.method == 'POST':
        if formset.errors:
            print(formset.errors)
        if formset.is_valid():
            for form in formset:
                form.save()
            return redirect('daily-transactions', date)
    return render(request,template,context)

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

def MultiDueSellCreateView(request, date):
    DueSellFormSet = formset_factory(DueSellForm, extra=0)
    formset = DueSellFormSet(request.POST or None, initial=[{'date':date}])
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Customer/duesell_formset.html"
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

class DueSellUpdateView(UpdateView):
    model = DueSell
    form_class = DueSellForm

class DueSellDeleteView(DeleteView):
    model = DueSell
    
    def get_success_url(self):
        return reverse_lazy('daily-transactions', kwargs={'date':self.object.date})