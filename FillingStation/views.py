from django.shortcuts import render

def home(request):
    template = 'base.html'
    return render(request, template)