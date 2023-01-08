from django.shortcuts import render, redirect
from django.forms import modelformset_factory
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
def DueCollectionFormsetView(request, date):
    qs = DueCollection.objects.filter(date=date)
    extra = 0 if qs.count() > 0 else 1
    DueCollectionFormSet = modelformset_factory(DueCollection, DueCollectionForm, extra=extra, can_delete=True)
    formset = DueCollectionFormSet(request.POST or None, queryset=qs)
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
            formset.save()
            return redirect('daily-transactions', date)
    return render(request,template,context)

# Due Sell
def DueSellFormsetView(request, date):
    qs = DueSell.objects.filter(date=date)
    extra = 0 if qs.count() > 0 else 1
    DueSellFormSet = modelformset_factory(DueSell, DueSellForm, extra=extra, can_delete=True)
    formset = DueSellFormSet(request.POST or None, queryset=qs)
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Customer/duesell_formset.html"
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