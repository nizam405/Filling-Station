from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from Customer.models import GroupofCompany
from Core.mixins import RedirectMixin

# Group of companies
class GroupofCompaniesView(RedirectMixin, CreateView, ListView):
    model = GroupofCompany
    fields = ['name','active']
    template_name = 'Customer/groupofcompanies.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        return context

class GroupofCompanyUpdateView(RedirectMixin, UpdateView, ListView):
    model = GroupofCompany
    fields = ['name','active']
    template_name = 'Customer/groupofcompanies.html'
    success_url = reverse_lazy('groupofcompanies')

class GroupofCompanyDeleteView(RedirectMixin, DeleteView):
    model = GroupofCompany
    success_url = reverse_lazy('groupofcompanies')

@login_required
def change_goc_status(requst, pk):
    goc = GroupofCompany.objects.get(pk=pk)
    goc.active = not goc.active
    goc.save()
    return redirect('groupofcompanies')