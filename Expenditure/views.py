from django.shortcuts import render, redirect
from django.forms import formset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
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

# Expenditure
# class ExpenditureListView(ListView):
#     model = Expenditure

# class ExpenditureCreateView(CreateView):
#     model = Expenditure
#     form_class = ExpenditureForm

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if 'date' in self.kwargs:
#             context['form'].initial = {'date':self.kwargs['date']}
#         return context

def MultiExpenditureCreateView(request, date):
    ExpenditureFormSet = formset_factory(ExpenditureForm, extra=0)
    formset = ExpenditureFormSet(request.POST or None, initial=[{'date':date}])
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
            for form in formset:
                form.save()
            return redirect('daily-transactions', date)
    return render(request,template,context)

class ExpenditureUpdateView(UpdateView):
    model = Expenditure
    form_class = ExpenditureForm

class ExpenditureDeleteView(DeleteView):
    model = Expenditure
    
    def get_success_url(self):
        return reverse_lazy('daily-transactions', kwargs={'date':self.object.date})
