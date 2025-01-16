from django.views.generic import TemplateView
from django.db.models import Sum

from Owner.models import Withdraw, Owner
from Core.mixins import NavigationMixin
        
  
class WithdrawLedger(NavigationMixin,TemplateView):
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


