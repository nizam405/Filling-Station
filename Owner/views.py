from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Owner

# Owner
class OwnerListView(ListView):
    model = Owner

class OwnerDetailView(DetailView):
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