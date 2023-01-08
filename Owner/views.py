from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView
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
def WithdrawFormsetView(request, date):
    qs = Withdraw.objects.filter(date=date)
    extra = 0 if qs.count() > 0 else 1
    WithdrawFormSet = modelformset_factory(Withdraw, WithdrawForm, extra=extra, can_delete=True)
    formset = WithdrawFormSet(request.POST or None, queryset=qs)
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Owner/withdraw_formset.html"
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
            # instances = formset.save(commit=False)
            # for obj in formset.deleted_objects:
            #     obj.delete()
            return redirect('daily-transactions', date)
    return render(request,template,context)
    
# Investment
# class InvestmentListView(ListView):
#     model = Investment

# class InvestmentCreateView(CreateView):
#     model = Investment
#     form_class = InvestmentForm

# class InvestmentUpdateView(UpdateView):
#     model = Investment
#     form_class = InvestmentForm

# class InvestmentDeleteView(DeleteView):
#     model = Investment
#     success_url = reverse_lazy('investment-list')
