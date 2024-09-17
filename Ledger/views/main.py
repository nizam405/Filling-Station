from django.views.generic import TemplateView
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin

from Expenditure.models import ExpenditureGroup, Expenditure
from Revenue.models import RevenueGroup, Revenue
from Owner.models import Withdraw, Owner
from Ledger.views.mixins import LedgerTopSheetMixin

class RevenueLedger(LoginRequiredMixin,LedgerTopSheetMixin,TemplateView):
    template_name = 'Ledger/revenue_column.html'

    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(**kwargs)
        # Collect data from mixin context
        from_date = context['target_date']
        to_date = context['to_date']

        revenues = Revenue.objects.filter(date__gte=from_date, date__lte=to_date)
        dates = [obj['date'] for obj in revenues.values('date').distinct()]
        dates = sorted(dates)
        
        data = []
        groups = revenues.values('group')
        revenue_groups = list(set(RevenueGroup.objects.get(pk=group['group']) for group in groups))
        revenue_groups = sorted(revenue_groups, key=lambda x:x.serial)
        context['revenue_groups'] = revenue_groups
        group_totals = {rg:0 for rg in revenue_groups}
        for day in dates:
            day_data = {'date':day}
            group_data = []
            day_total = 0
            for rg in revenue_groups:
                revenues_today = revenues.filter(date=day,group=rg)
                if revenues_today:
                    amount = revenues_today.aggregate(Sum('amount'))['amount__sum']
                else: amount = 0
                group_data.append(amount)
                day_total += amount
                group_totals[rg] += amount
            day_data['groups'] = group_data
            day_data['total'] = day_total
            # skip empty
            if day_total > 0:
                data.append(day_data)
        context['data'] = data
        context['totals'] = group_totals
        context['total'] = sum(group_totals.values())
            
        return context
        
class ExpenditureLedger(LoginRequiredMixin,LedgerTopSheetMixin,TemplateView):
    template_name = 'Ledger/expenditure.html'

    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(**kwargs)
        # Collect data from mixin context
        from_date = context['target_date']
        to_date = context['to_date']
        
        expenditures = Expenditure.objects.filter(date__gte=from_date, date__lte=to_date)
        dates = [obj['date'] for obj in expenditures.values('date').distinct()]
        dates = sorted(dates)

        data = []
        groups = expenditures.values('group')
        expenditure_groups = list(set(ExpenditureGroup.objects.get(pk=group['group']) for group in groups))
        expenditure_groups = sorted(expenditure_groups, key=lambda x:x.serial)
        context['expenditure_groups'] = expenditure_groups
        group_totals = {rg:0 for rg in expenditure_groups}
        for day in dates:
            day_data = {'date':day}
            group_data = []
            day_total = 0
            for rg in expenditure_groups:
                expenditures_today = expenditures.filter(date=day,group=rg)
                if expenditures_today:
                    amount = expenditures_today.aggregate(Sum('amount'))['amount__sum']
                else: amount = 0
                group_data.append(amount)
                day_total += amount
                group_totals[rg] += amount
            day_data['groups'] = group_data
            day_data['total'] = day_total
            # skip empty
            if day_total > 0:
                data.append(day_data)
        context['data'] = data
        context['totals'] = group_totals
        context['total'] = sum(group_totals.values())
            
        return context
  
class WithdrawLedger(LoginRequiredMixin,LedgerTopSheetMixin,TemplateView):
    template_name = 'Ledger/withdraw.html'

    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(**kwargs)
        # Collect data from mixin context
        from_date = context['target_date']
        to_date = context['to_date']
        
        withdraws = Withdraw.objects.filter(date__gte=from_date, date__lte=to_date)
        dates = [obj['date'] for obj in withdraws.values('date').distinct()]
        dates = sorted(dates)
        
        # Table heading
        owners = Owner.objects.all()
        context['owners'] = owners
        # data contains row of every day
        data = []
        totals = {owner.name:0 for owner in owners} # initial with 0
        # dates = all_dates_in_month(year,month)
        for day in dates:
            day_data = {'date':day}
            # owner_data contains per owner data on particular day
            owner_data = []
            day_total = 0
            for owner in owners:
                per_owner_data = {'withdraws':[]}
                withdraws_today = withdraws.filter(date=day,owner=owner)
                if withdraws_today:
                    # an owner can withdraw multiple times in a single day
                    for wd in withdraws_today:
                        per_owner_data['withdraws'].append({'detail':wd.detail,'amount':wd.amount})
                    amount = withdraws_today.aggregate(Sum('amount'))['amount__sum']
                else: amount = 0
                per_owner_data['amount'] = amount
                owner_data.append(per_owner_data)
                # Total
                totals[owner.name] += amount
                day_total += amount
            day_data['owners'] = owner_data
            day_data['total'] = day_total
            # skip empty
            if day_total > 0:
                data.append(day_data)
        context['data'] = data
        context['totals'] = totals
        context['grand_total'] = sum(totals.values())
            
        return context


