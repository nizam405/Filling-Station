from django.shortcuts import render, redirect
from django.forms import formset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Owner, Withdraw, Investment
from .forms import WithdrawForm, InvestmentForm

# Owner
class OwnerView(CreateView, ListView):
    model = Owner
    fields = '__all__'
    template_name = 'Owner/owners.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        return context

class OwnerUpdateView(UpdateView):
    model = Owner
    fields = '__all__'
    template_name = 'Owner/owners.html'
    success_url = reverse_lazy('owners')

class OwnerDeleteView(DeleteView):
    model = Owner
    success_url = reverse_lazy('owners')
    
# Withdraw
# class WithdrawListView(ListView):
#     model = Withdraw

# class WithdrawCreateView(CreateView):
#     model = Withdraw
#     form_class = WithdrawForm

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if 'date' in self.kwargs:
#             context['form'].initial = {'date':self.kwargs['date']}
#         return context

def MultiWithdrawCreateView(request, date):
    WithdrawFormSet = formset_factory(WithdrawForm, extra=0)
    formset = WithdrawFormSet(request.POST or None, initial=[{'date':date}])
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Owner/withdraw_formset.html"
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
