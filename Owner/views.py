from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Owner, Withdraw, Investment
from .forms import WithdrawForm, InvestmentForm

# Owner
class OwnerListView(ListView):
    model = Owner

class OwnerCreateView(CreateView):
    model = Owner
    fields = '__all__'

class OwnerUpdateView(UpdateView):
    model = Owner
    fields = '__all__'

class OwnerDeleteView(DeleteView):
    model = Owner
    success_url = reverse_lazy('owner-list')
    
# Withdraw
class WithdrawListView(ListView):
    model = Withdraw

class WithdrawCreateView(CreateView):
    model = Withdraw
    form_class = WithdrawForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'date' in self.kwargs:
            context['form'].initial = {'date':self.kwargs['date']}
        return context

class WithdrawUpdateView(UpdateView):
    model = Withdraw
    form_class = WithdrawForm

class WithdrawDeleteView(DeleteView):
    model = Withdraw
    
    def get_success_url(self):
        return reverse_lazy('daily-transactions', kwargs={'date':self.object.date})
    
# Investment
class InvestmentListView(ListView):
    model = Investment

class InvestmentCreateView(CreateView):
    model = Investment
    form_class = InvestmentForm

class InvestmentUpdateView(UpdateView):
    model = Investment
    form_class = InvestmentForm

class InvestmentDeleteView(DeleteView):
    model = Investment
    success_url = reverse_lazy('investment-list')
