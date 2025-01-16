from django.shortcuts import redirect, render
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Sum, Count
from django.contrib.auth.decorators import login_required

from Customer.models import Customer, GroupofCompany, DueSell, DueCollection, CustomerDue, GroupofCompanyDue
from Customer.forms import CustomerDueForm, GroupofCompanyDueForm, DueSellForm
from Product.views.purchase_sell import BasePurchaseSellView
from IncomeExpenditure.views import BaseIncomeExpenditureView
from Core.mixins import NavigationMixin

    
# Due Collection
class BaseDueCollectionView(BaseIncomeExpenditureView):
    model = DueCollection
    fields = ['customer','amount']
    template_name = 'Customer/duecollection.html'    

class DueCollectionCreateView(CreateView, BaseDueCollectionView):
    pass

class DueCollectionUpdateView(UpdateView, BaseDueCollectionView):
    pass

class DueCollectionDeleteView(DeleteView):
    # DueCollection এ থাকলে Delete করা যাবে না
    model = DueCollection

    def get(self,request,*args, **kwargs):
        return self.delete(request,*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('create-duecollection', kwargs={'date':self.kwargs['date']})

# Due Sell
class BaseDueSellView(BasePurchaseSellView):
    model = DueSell
    form_class = DueSellForm
    template_name = 'Customer/duesell.html'    

class DueSellCreateView(CreateView, BaseDueSellView):
    pass

class DueSellUpdateView(UpdateView, BaseDueSellView):
    pass

class DueSellDeleteView(DeleteView):
    # DueCollection এ থাকলে Delete করা যাবে না
    model = DueSell

    def get(self,request,*args, **kwargs):
        return self.delete(request,*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('create-duesell', kwargs={'date':self.kwargs['date']})

# Customer Balance (Group of company included)
class CustomerDueView(NavigationMixin, TemplateView):
    template_name = 'Customer/Ledger/customer_due.html'
     
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_current_bal = 0
        total_baddebt = 0

        # Group of Company - Current
        goc_balances = GroupofCompanyDue.objects.filter(date=self.date, bad_debt=False)
        context['goc_balances'] = goc_balances
        goc_total = goc_balances.aggregate(Sum('amount'))['amount__sum'] or 0
        total_current_bal += goc_total

        # Group of Company - Bad Debts
        goc_baddebts = GroupofCompanyDue.objects.filter(date=self.date, bad_debt=True)
        context['goc_baddebts'] = goc_baddebts
        goc_baddebt_total = goc_baddebts.aggregate(Sum('amount'))['amount__sum'] or 0
        total_baddebt += goc_baddebt_total

        # Customer Balances - Current
        cust_balances = CustomerDue.objects.filter(
            date=self.date, customer__group__isnull=True, bad_debt=False)
        if cust_balances:
            context['cust_balances'] = cust_balances
            cust_bal_total = cust_balances.aggregate(Sum('amount'))['amount__sum']
            total_current_bal += cust_bal_total
        # Customer Balances - Bad Debts
        cust_bad_debts = CustomerDue.objects.filter(
            date=self.date, customer__group__isnull=True, bad_debt=True)
        if cust_bad_debts:
            context['cust_bad_debts'] = cust_bad_debts
            total_cust_baddebt = cust_bad_debts.aggregate(Sum('amount'))['amount__sum']
            total_baddebt += total_cust_baddebt
        
        # Totals
        context['total_current_bal'] = total_current_bal
        context['total_baddebt'] = total_baddebt
        context['grand_total'] = total_current_bal + total_baddebt
        return context
    
@login_required
def customerBalanceFormsetView(request,date):
    # Group of Company Forms -----------------------------
    goc_balances = GroupofCompanyDue.objects.all()
    unique_goc = goc_balances.values('customer').annotate(
        total=Count('customer')).filter(total=1).values_list('customer', flat=True)
    unique_goc_bals = goc_balances.filter(customer__in=unique_goc)
    GocBalanceFormset = modelformset_factory(GroupofCompanyDue, GroupofCompanyDueForm, extra=0)
    goc_formset = GocBalanceFormset(request.POST or None, queryset=unique_goc_bals, prefix='goc')
    # Customer Forms -------------------------------------
    cust_balances = CustomerDue.objects.filter(customer__group__isnull=True)
    # শুধুমাত্র প্রাথমিক ব্যালেন্স পরিবর্তন করা যাবে, বাকি মাসের গুলো auto generate হবে
    unique_customers = cust_balances.values('customer').annotate(
        total=Count('customer')).filter(total=1).values_list('customer', flat=True)
    unique_balances = cust_balances.filter(customer__in=unique_customers)
    CustomerBalanceFormSet = modelformset_factory(CustomerDue, CustomerDueForm, extra=0)
    cust_formset = CustomerBalanceFormSet(request.POST or None, queryset=unique_balances, prefix='cust')
    cust_formset.initial = [{
        'customer':obj.customer,
        'amount':obj.amount, 
        'bad_debt': obj.bad_debt} for obj in unique_balances]
    template = "Customer/Ledger/customer_due_formset.html"
    context = {
        'goc_formset': goc_formset, 
        'cust_formset': cust_formset,
        'date':date,
        }

    if request.method == 'POST':
        if cust_formset.is_valid() and goc_formset.is_valid():
            goc_formset.save()
            cust_formset.save()
            return redirect('customer-due',date=date)
    return render(request,template,context)

@login_required
def markBaddebt(requst,date,pk,goc=False,unmark=False):
    if goc:
        objects = GroupofCompanyDue.objects.filter(date=date,customer=pk)
    else:
        objects = CustomerDue.objects.filter(date=date,customer=pk)
    for obj in objects:
        if not unmark:
            obj.bad_debt = True
        else: obj.bad_debt = False
        obj.save()
    return redirect('customer-due',date=date)
    
