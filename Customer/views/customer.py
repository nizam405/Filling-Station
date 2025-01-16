from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from Core.mixins import RedirectMixin
from Customer.models import Customer
from Customer.forms import CustomerForm

from django.views.generic import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

# Customer
class CustomerView(RedirectMixin, CreateView, ListView):
    model = Customer
    form_class = CustomerForm
    template_name = 'Customer/customers.html'
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        return context

class CustomerUpdateView(RedirectMixin, UpdateView, ListView):
    model = Customer
    fields = ['name','short_name','cust_type','group','mobile','serial']
    template_name = 'Customer/customers.html'
    success_url = reverse_lazy('customers')

class CustomerDeleteView(RedirectMixin, DeleteView):
    model = Customer
    success_url = reverse_lazy('customers')

@login_required
def change_cust_status(requst, pk):
    cust = Customer.objects.get(pk=pk)
    cust.active = not cust.active
    cust.save()
    return redirect('customers')