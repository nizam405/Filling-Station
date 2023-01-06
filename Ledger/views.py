from django.shortcuts import render
from django.views.generic import TemplateView

from Customer.models import Customer, GroupofCompany
from Product.models import Product

class LedgerList(TemplateView):
    template_name = 'Ledger/ledger_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Party
        group_of_company = GroupofCompany.objects.all()
        group_companies = []
        customers = Customer.objects.all()
        goc = customers.filter(cust_type='Group')
        for company in group_of_company:
            group_companies.append(
                {'name': company, 'companies': goc.filter(group=company)}
            )
        context['group_cumtomer'] = group_companies
        context['individual_customer'] = customers.filter(cust_type='Individual')
        
        # Products
        products = Product.objects.all()
        
        
        return context

