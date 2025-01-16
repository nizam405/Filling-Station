from django.views.generic import TemplateView, ListView
from django.db.models import Sum

from Customer.models import Customer, GroupofCompany, DueSell, DueCollection, CustomerDue, GroupofCompanyDue
from Product.models import Product
from Customer.forms import CustomerLedgerFilterForm, GroupofCompanyLedgerFilterForm
from Core.mixins import NavigationMixin
from .functions import get_customer_ledger_info
from Core.functions import accounts_dates_in_month

class CustomerTopSheet(NavigationMixin,TemplateView):
    template_name = 'Customer/Ledger/customer_topsheet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dataset = get_customer_ledger_info(self.from_date,self.date)
        for key,value in dataset.items():
            context[key] = value
        
        return context

class BaseCustomerLedger(NavigationMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        if 'customer' in self.request.GET:
            self.customer = self.cust_model.objects.get(pk=self.request.GET.get('customer'))
        elif 'customer' in self.kwargs:
            self.customer = self.cust_model.objects.get(pk=self.kwargs['customer'])
        else: self.customer = self.cust_model.objects.first()
        self.kwargs['customer'] = self.customer.pk
        return super().get(request, *args, **kwargs)
    
    def get_product_data(self, duesells):
        # Products Data
        products = set(sell.product for sell in duesells)
        product_dataset = []
        for product in products:
            product_info = {'product': product,'rate_info':[]}
            sells_of_product = duesells.filter(product=product)
            selling_rates = set(obj.selling_rate for obj in sells_of_product)
            for rate in selling_rates:
                sells_of_rate = sells_of_product.filter(selling_rate=rate)
                quantity = sells_of_rate.aggregate(Sum('quantity'))['quantity__sum']
                price = sells_of_rate.aggregate(Sum('price'))['price__sum']
                rate_info = {'quantity': quantity, 'rate': rate, 'price': price}
                product_info['rate_info'].append(rate_info)
            product_info['total'] = {
                'quantity': sells_of_product.aggregate(Sum('quantity'))['quantity__sum'],
                'price': sells_of_product.aggregate(Sum('price'))['price__sum']
            }
            product_dataset.append(product_info)
        return product_dataset

class CustomerLedger(BaseCustomerLedger):
    template_name = 'Customer/Ledger/customer_ledger.html'
    cust_model = Customer

    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['customer'] = self.customer
        context['filter_form'] = CustomerLedgerFilterForm(
            initial={'customer':self.customer,'date':self.date}
        )
        # Data
        initials = CustomerDue.objects.filter(customer=self.customer,date=self.from_date)
        duesells = DueSell.objects.filter(
            customer    = self.customer,
            date__gte   = self.from_date,
            date__lte   = self.date
        )
        duecollections = DueCollection.objects.filter(
            customer    = self.customer,
            date__gte   = self.from_date,
            date__lte   = self.date
        )
        initial_due = initials.last().amount or 0
        dates = accounts_dates_in_month(self.from_date,self.date)
        data = []
        for date in dates:
            daily_duesell = duesells.filter(date=date)
            daily_duecollection = duecollections.filter(date=date)
            if daily_duesell or daily_duecollection:
                duesell_amount = daily_duesell.aggregate(Sum('price'))['price__sum'] or 0
                duecollection_amount = daily_duecollection.aggregate(Sum('amount'))['amount__sum'] or 0
                current_due = initial_due + duesell_amount - duecollection_amount
                daily_data = {
                    'date': date,
                    'initial_due': initial_due,
                    'bad_debt': initials.last().bad_debt if initials else False,
                    'due_sells': daily_duesell,
                    'due_sells_amount': duesell_amount,
                    # 'due_collections': daily_duecollection,
                    'due_collections_amount': duecollection_amount,
                    'current_due': current_due
                }
                data.append(daily_data)
                initial_due = current_due

        context['object_list'] = data
        total = {
            'duesell': duesells.aggregate(Sum('price'))['price__sum'] or 0,
            'duecollection': duecollections.aggregate(Sum('amount'))['amount__sum'] or 0
        }
        context['total'] = total
        context['current_due'] = data[-1]['current_due'] if data else 0
        
        context['product_data'] = self.get_product_data(duesells)
        return context

class GroupofCompanyLedger(BaseCustomerLedger):
    template_name = 'Customer/Ledger/goc_ledger.html'
    cust_model = GroupofCompany
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['customer'] = self.customer
        context['filter_form'] = GroupofCompanyLedgerFilterForm(
            initial = {'customer':self.customer, 'date':self.date}
        )

        # Data
        initials = GroupofCompanyDue.objects.filter(customer=self.customer,date=self.from_date)
        duesells = DueSell.objects.filter(customer__group=self.customer, date__gte=self.from_date, date__lte=self.date)
        duecollections = DueCollection.objects.filter(customer__group=self.customer, date__gte=self.from_date, date__lte=self.date)
        sub_companies = Customer.objects.filter(group=self.customer)
        
        initial_due = initials.last().amount or 0
        dates = accounts_dates_in_month(self.from_date,self.date)
        data = []
        for date in dates:
            daily_duesell = duesells.filter(date=date)
            daily_duecollection = duecollections.filter(date=date)
            if daily_duesell or daily_duecollection:
                duesell_amount = daily_duesell.aggregate(Sum('price'))['price__sum'] or 0
                duecollection_amount = daily_duecollection.aggregate(Sum('amount'))['amount__sum'] or 0
                current_due = initial_due + duesell_amount - duecollection_amount
                sub_company_duesell = []
                for company in sub_companies:
                    company_duesell = daily_duesell.filter(customer=company)
                    company_duesell_amount = company_duesell.aggregate(Sum('price'))['price__sum'] or 0
                    sub_company_duesell.append({
                        'due_sells': company_duesell,
                        'due_sells_amount': company_duesell_amount
                    })
                daily_data = {
                    'date': date,
                    'initial_due': initial_due,
                    'bad_debt': initials.last().bad_debt if initials else False,
                    'subcompanies_duesell': sub_company_duesell,
                    # 'due_sells': daily_duesell,
                    'due_sells_amount': duesell_amount,
                    'due_collections_amount': duecollection_amount,
                    'current_due': current_due
                }
                data.append(daily_data)
                initial_due = current_due

        context['object_list'] = data
        
        sub_companies_data = list()
        for cust in sub_companies:
            cust_duesell = duesells.filter(customer=cust)
            sub_companies_data.append({
                'customer': cust,
                'total': cust_duesell.aggregate(Sum('price'))['price__sum'] or 0
            })

        context['sub_companies_data'] = sub_companies_data
        
        total = {
            'duesell': duesells.aggregate(Sum('price'))['price__sum'] or 0,
            'duecollection': duecollections.aggregate(Sum('amount'))['amount__sum'] or 0
        }
        context['total'] = total
        context['current_due'] = data[-1]['current_due'] if data else 0
        
        context['product_data'] = self.get_product_data(duesells)

        return context
