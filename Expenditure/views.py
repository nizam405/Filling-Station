from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Expenditure, ExpenditureGroup
from .forms import ExpenditureForm

# Expenditure Group
class ExpenditureGroupListView(ListView):
    model = ExpenditureGroup

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

class ExpenditureUpdateView(UpdateView):
    model = Expenditure
    form_class = ExpenditureForm

class ExpenditureDeleteView(DeleteView):
    model = Expenditure
    success_url = reverse_lazy('expenditure-list')
