from django.shortcuts import render
from django.urls import reverse_lazy
from datetime import date
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Expenditure, ExpenditureGroup
from .forms import ExpenditureForm

# Expenditure Group
class ExpenditureGroupListView(ListView):
    model = ExpenditureGroup
    fields = '__all__'

class ExpenditureGroupCreateView(CreateView):
    model = ExpenditureGroup
    fields = '__all__'

class ExpenditureGroupUpdateView(UpdateView):
    model = ExpenditureGroup
    fields = '__all__'

class ExpenditureGroupDeleteView(DeleteView):
    model = ExpenditureGroup
    success_url = reverse_lazy('expendituregroup-list')

# Expenditure
class ExpenditureListView(ListView):
    model = Expenditure

class ExpenditureCreateView(CreateView):
    model = Expenditure
    form_class = ExpenditureForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'date' in self.kwargs:
            context['form'].initial = {'date':self.kwargs['date']}
        return context

class ExpenditureUpdateView(UpdateView):
    model = Expenditure
    form_class = ExpenditureForm

class ExpenditureDeleteView(DeleteView):
    model = Expenditure
    
    def get_success_url(self):
        return reverse_lazy('daily-transactions', kwargs={'date':self.object.date})
