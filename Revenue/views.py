from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Revenue, RevenueGroup
from .forms import RevenueForm

# Revenue Group
class RevenueGroupListView(ListView):
    model = RevenueGroup

class RevenueGroupCreateView(CreateView):
    model = RevenueGroup
    fields = '__all__'

class RevenueGroupUpdateView(UpdateView):
    model = RevenueGroup
    fields = '__all__'

class RevenueGroupDeleteView(DeleteView):
    model = RevenueGroup
    success_url = reverse_lazy('revenueegroup-list')

# Revenue
class RevenueListView(ListView):
    model = Revenue

class RevenueCreateView(CreateView):
    model = Revenue
    form_class = RevenueForm

class RevenueUpdateView(UpdateView):
    model = Revenue
    form_class = RevenueForm

class RevenueDeleteView(DeleteView):
    model = Revenue
    success_url = reverse_lazy('revenue-list')
