from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from Core.mixins import RedirectMixin
from Core.views import RestrictedDeleteView
from Product.models import Product

# Product
class BaseProductView(RedirectMixin, ListView):
    model = Product
    fields = ['name','short_name','category','packaged','capacity']
    template_name = 'Product/products.html'
    success_url = reverse_lazy('products')

class ProductView(CreateView, BaseProductView):
    success_url = '.'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        return context

class ProductUpdateView(UpdateView, BaseProductView): pass

def change_product_status(request, pk):
    product = Product.objects.get(pk=pk)
    product.active = not product.active
    product.save()
    return redirect('products')

class ProductDeleteView(RestrictedDeleteView):
    model = Product
    success_url = reverse_lazy('products')
