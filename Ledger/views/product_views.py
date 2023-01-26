from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import CreateView
from django.db.models import Sum
import pybengali
import datetime

from Customer.models import Customer, GroupofCompany, DueSell, DueCollection
from Product.models import Product
from Transaction.models import CashBalance
from Ledger.models import Storage

class StorageView(CreateView, ListView):
    model = Storage
    fields = '__all__'
    template_name = 'Ledger/storage.html'
    success_url = '.'

    def get_initial(self):
        initial = super().get_initial()
        if 'product_id' in self.kwargs:
            initial.update({'product':self.kwargs['product_id']})
        return initial