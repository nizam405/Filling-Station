from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Expenditure, ExpenditureGroup
from .forms import ExpenditureForm

# Expenditure Group
class ExpenditureGroupView(CreateView, ListView):
    model = ExpenditureGroup
    fields = '__all__'
    template_name = 'Expenditure/expenditure_group.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        return context

class ExpenditureGroupUpdateView(UpdateView, ListView):
    model = ExpenditureGroup
    fields = '__all__'
    template_name = 'Expenditure/expenditure_group.html'
    success_url = reverse_lazy('expenditure-group')

class ExpenditureGroupDeleteView(DeleteView):
    model = ExpenditureGroup
    success_url = reverse_lazy('expenditure-group')

def ExpenditureFormsetView(request, date):
    qs = Expenditure.objects.filter(date=date)
    extra = 0 if qs.count() > 0 else 1
    ExpenditureFormSet = modelformset_factory(Expenditure, ExpenditureForm, extra=extra, can_delete=True)
    formset = ExpenditureFormSet(request.POST or None, queryset=qs)
    formset.initial = [{'date':date} for i in range(0,extra)]
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Expenditure/expenditure_formset.html"
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
