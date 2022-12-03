from django.shortcuts import render
from django.views.generic.base import RedirectView

class HomeView(RedirectView):
    pattern_name = 'daily-transactions'