from django.shortcuts import render
from django.urls import reverse_lazy
from datetime import date
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = date.today()
        return context

class RevenueCreateView(CreateView):
    model = Revenue
    form_class = RevenueForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'date' in self.kwargs:
            context['form'].initial = {'date':self.kwargs['date']}
        return context

class RevenueUpdateView(UpdateView):
    model = Revenue
    form_class = RevenueForm

class RevenueDeleteView(DeleteView):
    model = Revenue
    
    def get_success_url(self):
        return reverse_lazy('daily-transactions', kwargs={'date':self.object.date})
