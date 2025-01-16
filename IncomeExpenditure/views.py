from django.shortcuts import redirect
from django.urls import reverse_lazy
from Core.mixins import NavigationMixin
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Sum, Max

from Core.mixins import RedirectMixin, NavigationMixin
from .models import Expenditure, ExpenditureGroup, Income, IncomeGroup, BaseIncomeExpenditure, BaseIncomeExpenditureGroup
from Owner.functions import generate_net_profit, generate_owners_equity

# Group
class BaseGroupView(RedirectMixin, ListView):
    fields = '__all__'
    template_name = 'IncomeExpenditure/group.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['container_class'] = 'hidden'
        context['model'] = self.model.__name__
        return context
    
    def get_initial(self):
        # Auto Increment the serial field
        if isinstance(self, CreateView):
            max_serial = self.model.objects.aggregate(Max('serial'))['serial__max']
            return {'serial': max_serial+1}
    
# Expenditure Group
class BaseExpenditureGroupView(BaseGroupView):
    model = ExpenditureGroup
    success_url = reverse_lazy('create-expenditure-group')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_url'] = self.success_url
        context['update_url_name'] = 'update-expenditure-group'
        context['delete_url_name'] = 'delete-expenditure-group'
        return context

class ExpenditureGroupCreateView(CreateView, BaseExpenditureGroupView): pass
class ExpenditureGroupUpdateView(UpdateView, BaseExpenditureGroupView): pass

# Income Group
class BaseIncomeGroupView(BaseGroupView):
    model = IncomeGroup
    success_url = reverse_lazy('create-income-group')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_url'] = self.success_url
        context['update_url_name'] = 'update-income-group'
        context['delete_url_name'] = 'delete-income-group'
        return context

class IncomeGroupCreateView(CreateView, BaseIncomeGroupView): pass
class IncomeGroupUpdateView(UpdateView, BaseIncomeGroupView): pass

# Group Delete
class BaseGroupDeleteView(RedirectMixin, DeleteView):
    template_name = 'IncomeExpenditure/group_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = self.model.__name__
        context['base_url'] = self.get_success_url()
        return context
    
    def get_success_url(self):
        return self.get_object().get_absolute_url()

class IncomeGroupDeleteView(BaseGroupDeleteView):
    model = IncomeGroup
class ExpenditureGroupDeleteView(BaseGroupDeleteView):
    model = ExpenditureGroup

# 
class BaseIncomeExpenditureView(RedirectMixin, ListView):
    fields = ['group','detail','amount']
    template_name = 'IncomeExpenditure/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = self.model.__name__
        context['date'] = self.kwargs['date']
        qs = self.get_queryset()
        context['total'] = qs.aggregate(Sum('amount'))['amount__sum'] if qs else 0
        return context
    
    def get_queryset(self):
        return self.model.objects.filter(date=self.kwargs['date'])

# Income View
class BaseIncomeView(BaseIncomeExpenditureView):
    model = Income

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_url'] = self.get_success_url()
        context['update_url_name'] = 'update-income'
        context['delete_url_name'] = 'delete-income'
        context['create_group_url'] = reverse_lazy('create-income-group')
        return context

    def get_success_url(self):
        return reverse_lazy('create-income', kwargs={'date':self.kwargs['date']})

class IncomeCreateView(CreateView, BaseIncomeView): pass
class IncomeUpdateView(UpdateView, BaseIncomeView): pass

# Expenditure View
class BaseExpenditureView(BaseIncomeExpenditureView):
    model = Expenditure

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_url'] = self.get_success_url()
        context['update_url_name'] = 'update-expenditure'
        context['delete_url_name'] = 'delete-expenditure'
        context['create_group_url'] = reverse_lazy('create-expenditure-group')
        return context

    def get_success_url(self):
        return reverse_lazy('create-expenditure', kwargs={'date':self.kwargs['date']})

class ExpenditureCreateView(CreateView, BaseExpenditureView): pass
class ExpenditureUpdateView(UpdateView, BaseExpenditureView): pass

# Income/Expenditure Delete
class BaseIncomeExpenditureDeleteView(RedirectMixin, DeleteView):
    def get(self, request, *args, **kwargs):
        self.delete(request)
        return redirect(self.get_success_url())
    
class ExpenditureDeleteView(BaseIncomeExpenditureDeleteView): 
    model = Expenditure
    
    def get_success_url(self):
        return reverse_lazy('create-expenditure',kwargs={'date':self.kwargs['date']})
    
class IncomeDeleteView(BaseIncomeExpenditureDeleteView): 
    model = Income
    
    def get_success_url(self):
        return reverse_lazy('create-income',kwargs={'date':self.kwargs['date']})
    
# Ledger
class BaseLedgerColumnView(NavigationMixin, TemplateView):
    template_name = 'IncomeExpenditure/ledger_column.html'
    model = BaseIncomeExpenditure
    model_group = BaseIncomeExpenditureGroup

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        
        objects = self.model.objects.filter(date__gte=self.from_date, date__lte=self.date)
        dates = [obj['date'] for obj in objects.values('date').distinct()]
        dates = sorted(dates)

        data = []
        groups = list(set(object.group for object in objects))
        context['group_names'] = [group.name for group in groups]
        groups = sorted(groups, key=lambda x:x.serial)
        group_totals = {group:0 for group in groups}
        for day in dates:
            day_data = {'date':day}
            group_data = []
            day_total = 0
            for group in groups:
                transactions_today = objects.filter(date=day,group=group)
                if transactions_today:
                    amount = transactions_today.aggregate(Sum('amount'))['amount__sum']
                else: amount = 0
                group_data.append(amount)
                day_total += amount
                group_totals[group] += amount
            day_data['groups'] = group_data
            day_data['total'] = day_total
            # skip empty
            if day_total > 0:
                data.append(day_data)
        context['data'] = data
        context['totals'] = group_totals
        context['total'] = sum(group_totals.values())
            
        return context
    
class ExpenditureLedgerColumnView(BaseLedgerColumnView):
    model = Expenditure
    model_group = ExpenditureGroup
    
class IncomeLedgerColumnView(BaseLedgerColumnView):
    model = Income
    model_group = IncomeGroup


class IncomeStatementView(NavigationMixin,TemplateView):
    template_name = 'IncomeExpenditure/incomestatement.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(generate_net_profit(self.from_date, self.date))
        context.update(generate_owners_equity(self.from_date, self.date))
        return context