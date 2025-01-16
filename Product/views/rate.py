from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from Core.mixins import RedirectMixin
from Core.views import RestrictedDeleteView
from Product.models import Product, SellingRateVariant, SellingRate, PurchaseRateVariant, PurchaseRate
from Product.forms import PurchaseRateForm, SellingRateForm

class BaseRateVariant(RedirectMixin, ListView):
    fields = '__all__'
    template_name = 'Product/rate_variant.html'

class BasePurchaseRateVariantView(BaseRateVariant):
    model = PurchaseRateVariant

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['subject'] = 'ক্রয়মূল্যের'
        context['base_pattern'] = 'purchase-rate-variant'
        context['update_pattern'] = 'update-purchase-rate-variant'
        context['delete_pattern'] = 'delete-purchase-rate-variant'
        return context

# Purchase Rate Variant
class PurchaseRateVariantCreateView(CreateView, BasePurchaseRateVariantView):pass

class PurchaseRateVariantUpdateView(UpdateView, BasePurchaseRateVariantView):pass

class PurchaseRateVariantDeleteView(RestrictedDeleteView):
    model = PurchaseRateVariant
    success_url = reverse_lazy('purchase-rate-variant')

# Selling Rate Variant
class BaseSellingRateVariantView(BaseRateVariant):
    model = SellingRateVariant

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['subject'] = 'বিক্রয়মূল্যের'
        context['base_pattern'] = 'selling-rate-variant'
        context['update_pattern'] = 'update-selling-rate-variant'
        context['delete_pattern'] = 'delete-selling-rate-variant'
        return context

class SellingRateVariantCreateView(CreateView, BaseSellingRateVariantView):pass

class SellingRateVariantUpdateView(UpdateView, BaseSellingRateVariantView):pass

class SellingRateVariantDeleteView(RestrictedDeleteView):
    model = SellingRateVariant
    success_url = reverse_lazy('selling-rate-variant')

# Rate
class BaseRateView(RedirectMixin, ListView):
    paginate_by = 20
    template_name = 'Product/rate.html'

    def get_product(self):
        product = Product.objects.get(pk=self.kwargs['product'])
        return product
    
    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context['product'] = self.get_product()
        if self.model==PurchaseRate:
            context['rate_model'] = 'ক্রয়মূল্য'
            context['base_url'] = 'create-purchase-rate'
            context['update_url'] = 'update-purchase-rate'
            context['delete_url'] = 'delete-purchase-rate'
            context['variant_url'] = 'purchase-rate-variant'
            context['rate_variants'] = PurchaseRateVariant.objects.all()
        elif self.model==SellingRate:
            context['rate_model'] = 'বিক্রয়মূল্য'
            context['base_url'] = 'create-selling-rate'
            context['update_url'] = 'update-selling-rate'
            context['delete_url'] = 'delete-selling-rate'
            context['variant_url'] = 'selling-rate-variant'
            context['rate_variants'] = SellingRateVariant.objects.all()
        return context
    
    def get_queryset(self):
        rates = self.model.objects.filter(product=self.get_product())
        if 'variant' in self.kwargs:
            rates = rates.filter(variant=self.kwargs['variant'])
        return rates
    
    def form_valid(self, form):
        form.instance.product = self.get_product()
        return super().form_valid(form)

# Purchase Rate
class BasePurchaseRateView(BaseRateView):
    model = PurchaseRate
    form_class = PurchaseRateForm

class PurchaseRateCreateView(CreateView, BasePurchaseRateView):pass

class PurchaseRateUpdateView(UpdateView,BasePurchaseRateView):pass

class PurchaseRateDeleteView(RestrictedDeleteView):
    model = PurchaseRate

    def get_success_url(self):
        return reverse_lazy('create-purchase-rate', kwargs={'product': self.kwargs['product']})

# Selling Rate
class BaseSellingRateView(BaseRateView):
    model = SellingRate
    form_class = SellingRateForm

class SellingRateCreateView(CreateView, BaseSellingRateView):pass

class SellingRateUpdateView(UpdateView,BaseSellingRateView):pass

class SellingRateDeleteView(RestrictedDeleteView):
    model = SellingRate

    def get_success_url(self):
        return reverse_lazy('create-selling-rate', kwargs={'product': self.kwargs['product']})
