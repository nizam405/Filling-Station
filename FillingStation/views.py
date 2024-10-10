from django.shortcuts import render
from django.views.generic.base import RedirectView
from Core.models import Settings

class HomeView(RedirectView):
    if Settings.objects.exists():
        pattern_name = 'daily-transactions'
    else: pattern_name = 'create-settings'