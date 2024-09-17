from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Customer, DueSell, DueCollection, GroupofCompany
from .forms import DueCollectionForm, DueSellForm, CustomerForm
from Transaction.mixins import BalanceRequiredMixin

# Group of companies
class GroupofCompaniesView(LoginRequiredMixin, BalanceRequiredMixin, CreateView, ListView):
    model = GroupofCompany
    fields = ['name','active']
    template_name = 'Customer/groupofcompanies.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        return context

class GroupofCompanyUpdateView(LoginRequiredMixin, BalanceRequiredMixin, UpdateView, ListView):
    model = GroupofCompany
    fields = ['name','active']
    template_name = 'Customer/groupofcompanies.html'
    success_url = reverse_lazy('groupofcompanies')

class GroupofCompanyDeleteView(LoginRequiredMixin, BalanceRequiredMixin, DeleteView):
    model = GroupofCompany
    success_url = reverse_lazy('groupofcompanies')

@login_required
def change_goc_status(requst, pk):
    goc = GroupofCompany.objects.get(pk=pk)
    goc.active = not goc.active
    goc.save()
    return redirect('groupofcompanies')

# Customer
class CustomerView(LoginRequiredMixin, BalanceRequiredMixin, CreateView, ListView):
    model = Customer
    form_class = CustomerForm
    template_name = 'Customer/customers.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        return context

class CustomerUpdateView(LoginRequiredMixin, BalanceRequiredMixin, UpdateView, ListView):
    model = Customer
    fields = ['name','short_name','cust_type','group','mobile','serial']
    template_name = 'Customer/customers.html'
    success_url = reverse_lazy('customers')

class CustomerDeleteView(LoginRequiredMixin, BalanceRequiredMixin, DeleteView):
    model = Customer
    success_url = reverse_lazy('customers')

@login_required
def change_cust_status(requst, pk):
    cust = Customer.objects.get(pk=pk)
    cust.active = not cust.active
    cust.save()
    return redirect('customers')
    
# Due Collection
@login_required
def DueCollectionFormsetView(request, date):
    qs = DueCollection.objects.filter(date=date)
    extra = 0 if qs.count() > 0 else 1
    DueCollectionFormSet = modelformset_factory(DueCollection, DueCollectionForm, extra=extra, can_delete=True)
    formset = DueCollectionFormSet(request.POST or None, queryset=qs)
    formset.initial = [{'date':date} for i in range(0,extra)]
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Customer/duecollection_formset.html"
    context = {
        'formset': formset, 
        'empty_form': empty_form,
        'date': date,
        }

    if request.method == 'POST':
        # if formset.errors:
        #     print(formset.errors)
        if formset.is_valid():
            formset.save()
            return redirect('daily-transactions', date)
    return render(request,template,context)

# Due Sell
@login_required
def DueSellFormsetView(request, date):
    qs = DueSell.objects.filter(date=date)
    extra = 0 if qs.count() > 0 else 1
    DueSellFormSet = modelformset_factory(DueSell, DueSellForm, extra=extra, can_delete=True)
    formset = DueSellFormSet(request.POST or None, queryset=qs)
    formset.initial = [{'date':date} for i in range(0,extra)]
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Customer/duesell_formset.html"
    context = {
        'formset': formset, 
        'empty_form': empty_form,
        'date': date,
        }

    if request.method == 'POST':
        # if formset.errors:
        #     print(formset.errors)
        if formset.is_valid():
            formset.save()
            return redirect('daily-transactions', date)
    return render(request,template,context)