from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView
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

def RevenueFormsetView(request, date):
    qs = Revenue.objects.filter(date=date)
    extra = 0 if qs.count() > 0 else 1
    RevenueFormSet = modelformset_factory(Revenue, RevenueForm, extra=extra, can_delete=True)
    formset = RevenueFormSet(request.POST or None, queryset=qs)
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Revenue/revenue_formset.html"
    context = {
        'formset': formset, 
        'empty_form': empty_form,
        'date': date,
        }

    if request.method == 'POST':
        # if formset.errors:
        #     print(formset.errors)
        if formset.is_valid():
            formset.save()
            # instances = formset.save(commit=False)
            # for obj in formset.deleted_objects:
            #     obj.delete()
            return redirect('daily-transactions', date)
    return render(request,template,context)