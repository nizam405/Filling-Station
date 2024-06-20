from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class DocumentationHome(LoginRequiredMixin, TemplateView):
    template_name = 'Documentation/home.html'