from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.db.models import Sum
import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from Expenditure.models import ExpenditureGroup, Expenditure
from Revenue.models import RevenueGroup, Revenue
from Owner.models import Withdraw, Owner
from Ledger.forms import DateFilterForm
from Transaction.models import CashBalance
from Core.choices import last_day_of_month

class RevenueLedger(LoginRequiredMixin,TemplateView):
    template_name = 'Ledger/revenue.html'

    def get(self, request, *args, **kwargs):
        # maintain cashbalance date to avoid blank page
        if CashBalance.objects.exists():
            first_bal_date = CashBalance.objects.order_by('date').first().date
            last_bal_date = CashBalance.objects.order_by('date').last().date

            first_date = datetime.date(first_bal_date.year,first_bal_date.month,1)
            first_date = first_date + datetime.timedelta(days=31)
        else:
            return redirect('daily-transactions')

        if 'month' in self.request.GET and 'year' in self.request.GET:
            self.kwargs['month'] = int(self.request.GET['month'])
            self.kwargs['year'] = int(self.request.GET['year'])
        elif 'month' not in self.kwargs and 'year' not in self.kwargs:
            self.kwargs['month'] = last_bal_date.month
            self.kwargs['year'] = last_bal_date.year
        month = self.kwargs['month']
        year = self.kwargs['year']
        
        target_date = datetime.date(year,month,1)
        # For very first time
        if last_bal_date.year == first_bal_date.year and last_bal_date.month == first_bal_date.month:
            target_date = last_bal_date
        # Dont let go future
        if target_date > last_bal_date:
            return redirect('revenue-ledger', month=last_bal_date.month, year=last_bal_date.year)
        elif target_date <= first_bal_date:
            return redirect('revenue-ledger', month=first_date.month, year=first_date.year)

        prev_month_date = target_date - datetime.timedelta(days=1)
        self.kwargs['prev_month'] = prev_month_date.month
        self.kwargs['prev_month_year'] = prev_month_date.year
        # here num_days+7 to make sure it goes to next month
        self.kwargs['next_date'] = target_date + datetime.timedelta(days=31)

        return super().get(request, *args, **kwargs)
    
    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(**kwargs)
        form = DateFilterForm(self.request.GET or self.kwargs or None)
        context['filter_form'] = form
        context['month'] = self.kwargs['month']
        context['year'] = self.kwargs['year']
        context['prev'] = {
            'month': self.kwargs['prev_month'],
            'year': self.kwargs['prev_month_year']
        }
        context['next'] = {
            'month': self.kwargs['next_date'].month,
            'year': self.kwargs['next_date'].year
        }
        year = int(self.kwargs['year'])
        month = int(self.kwargs['month'])
        from_date = datetime.date(year,month,1)
        to_date = CashBalance.objects.filter(date__month=month,date__year=year).order_by('date').last().date
        last_day = last_day_of_month(year,month)
        context['status'] = last_day == to_date
        context['to_date'] = to_date

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
        
class ExpenditureLedger(LoginRequiredMixin,TemplateView):
    template_name = 'Ledger/expenditure.html'

    def get(self, request, *args, **kwargs):
        # maintain cashbalance date to avoid blank page
        if CashBalance.objects.exists():
            first_bal_date = CashBalance.objects.order_by('date').first().date
            last_bal_date = CashBalance.objects.order_by('date').last().date

            first_date = datetime.date(first_bal_date.year,first_bal_date.month,1)
            first_date = first_date + datetime.timedelta(days=31)
        else:
            return redirect('daily-transactions')

        if 'month' in self.request.GET and 'year' in self.request.GET:
            self.kwargs['month'] = int(self.request.GET['month'])
            self.kwargs['year'] = int(self.request.GET['year'])
        elif 'month' not in self.kwargs and 'year' not in self.kwargs:
            self.kwargs['month'] = last_bal_date.month
            self.kwargs['year'] = last_bal_date.year
        month = self.kwargs['month']
        year = self.kwargs['year']
        
        target_date = datetime.date(year,month,1)
        # For very first time
        if last_bal_date.year == first_bal_date.year and last_bal_date.month == first_bal_date.month:
            target_date = last_bal_date
        # Dont let go future
        if target_date > last_bal_date:
            return redirect('expenditure-ledger', month=last_bal_date.month, year=last_bal_date.year)
        elif target_date <= first_bal_date:
            return redirect('expenditure-ledger', month=first_date.month, year=first_date.year)

        prev_month_date = target_date - datetime.timedelta(days=1)
        self.kwargs['prev_month'] = prev_month_date.month
        self.kwargs['prev_month_year'] = prev_month_date.year
        # here num_days+7 to make sure it goes to next month
        self.kwargs['next_date'] = target_date + datetime.timedelta(days=31)

        return super().get(request, *args, **kwargs)
    
    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(**kwargs)
        form = DateFilterForm(self.request.GET or self.kwargs or None)
        context['filter_form'] = form
        context['month'] = self.kwargs['month']
        context['year'] = self.kwargs['year']
        context['prev'] = {
            'month': self.kwargs['prev_month'],
            'year': self.kwargs['prev_month_year']
        }
        context['next'] = {
            'month': self.kwargs['next_date'].month,
            'year': self.kwargs['next_date'].year
        }
        year = int(self.kwargs['year'])
        month = int(self.kwargs['month'])
        from_date = datetime.date(year,month,1)
        to_date = CashBalance.objects.filter(date__month=month,date__year=year).order_by('date').last().date
        last_day = last_day_of_month(year,month)
        context['status'] = last_day == to_date
        context['to_date'] = to_date
        
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
  
class WithdrawLedger(LoginRequiredMixin,TemplateView):
    template_name = 'Ledger/withdraw.html'

    def get(self, request, *args, **kwargs):
        # maintain cashbalance date to avoid blank page
        if CashBalance.objects.exists():
            first_bal_date = CashBalance.objects.order_by('date').first().date
            last_bal_date = CashBalance.objects.order_by('date').last().date

            first_date = datetime.date(first_bal_date.year,first_bal_date.month,1)
            first_date = first_date + datetime.timedelta(days=31)
        else:
            return redirect('daily-transactions')

        if 'month' in self.request.GET and 'year' in self.request.GET:
            self.kwargs['month'] = int(self.request.GET['month'])
            self.kwargs['year'] = int(self.request.GET['year'])
        elif 'month' not in self.kwargs and 'year' not in self.kwargs:
            self.kwargs['month'] = last_bal_date.month
            self.kwargs['year'] = last_bal_date.year
        month = self.kwargs['month']
        year = self.kwargs['year']
        
        target_date = datetime.date(year,month,1)
        # For very first time
        if last_bal_date.year == first_bal_date.year and last_bal_date.month == first_bal_date.month:
            target_date = last_bal_date
        # Dont let go future
        if target_date > last_bal_date:
            return redirect('withdraw-ledger', month=last_bal_date.month, year=last_bal_date.year)
        elif target_date <= first_bal_date:
            return redirect('withdraw-ledger', month=first_date.month, year=first_date.year)

        prev_month_date = target_date - datetime.timedelta(days=1)
        self.kwargs['prev_month'] = prev_month_date.month
        self.kwargs['prev_month_year'] = prev_month_date.year
        # here num_days+7 to make sure it goes to next month
        self.kwargs['next_date'] = target_date + datetime.timedelta(days=31)

        return super().get(request, *args, **kwargs)
    
    def get_context_data(self,*args, **kwargs):
        context = super().get_context_data(**kwargs)
        form = DateFilterForm(self.request.GET or self.kwargs or None)
        context['filter_form'] = form
        context['month'] = self.kwargs['month']
        context['year'] = self.kwargs['year']
        context['prev'] = {
            'month': self.kwargs['prev_month'],
            'year': self.kwargs['prev_month_year']
        }
        context['next'] = {
            'month': self.kwargs['next_date'].month,
            'year': self.kwargs['next_date'].year
        }
        year = int(self.kwargs['year'])
        month = int(self.kwargs['month'])
        from_date = datetime.date(year,month,1)
        to_date = CashBalance.objects.filter(date__month=month,date__year=year).order_by('date').last().date
        last_day = last_day_of_month(year,month)
        context['status'] = last_day == to_date
        context['to_date'] = to_date
        
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


