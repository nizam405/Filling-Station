from django.shortcuts import render, redirect
from django.forms import formset_factory
from django.urls import reverse_lazy
from datetime import date
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Revenue, RevenueGroup
from .forms import RevenueForm

# Revenue Group
class RevenueGroupView(CreateView, ListView):
    model = RevenueGroup
    fields = '__all__'
    template_name = 'Revenue/revenue_group.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        return context

class RevenueGroupUpdateView(UpdateView, ListView):
    model = RevenueGroup
    fields = '__all__'
    template_name = 'Revenue/revenue_group.html'
    success_url = reverse_lazy('revenue-group')

class RevenueGroupDeleteView(DeleteView):
    model = RevenueGroup
    success_url = reverse_lazy('revenue-group')

# Revenue
# class RevenueListView(ListView):
#     model = Revenue

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['date'] = date.today()
#         return context

# class RevenueCreateView(CreateView):
#     model = Revenue
#     form_class = RevenueForm

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if 'date' in self.kwargs:
#             context['form'].initial = {'date':self.kwargs['date']}
#         return context

def MultiRevenueCreateView(request, date):
    RevenueFormSet = formset_factory(RevenueForm, extra=0)
    formset = RevenueFormSet(request.POST or None, initial=[{'date':date}])
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Revenue/revenue_formset.html"
    context = {
        'formset': formset, 
        'empty_form': empty_form,
        'date': date,
        }

    if request.method == 'POST':
        if formset.errors:
            print(formset.errors)
        if formset.is_valid():
            for form in formset:
                form.save()
            return redirect('daily-transactions', date)
    return render(request,template,context)

class RevenueUpdateView(UpdateView):
    model = Revenue
    form_class = RevenueForm

class RevenueDeleteView(DeleteView):
    model = Revenue
    
    def get_success_url(self):
        return reverse_lazy('daily-transactions', kwargs={'date':self.object.date})
