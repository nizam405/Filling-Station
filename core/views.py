from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from django.views.generic.base import TemplateView
from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from .models import Settings
from .forms import SettingsForm
from .mixins import RedirectMixin

# Create your views here.
class SettingsCreateView(RedirectMixin, CreateView):
    model = Settings
    form_class = SettingsForm
    template_name = 'Core/settings.html'
    success_url = reverse_lazy('daily-transactions')

class SettingsUpdateView(RedirectMixin, UpdateView):
    model = Settings
    form_class = SettingsForm
    template_name = 'Core/settings.html'
    success_url = reverse_lazy('daily-transactions')