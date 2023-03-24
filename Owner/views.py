from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .models import Owner, Withdraw, Investment, OwnersEquity, FixedAsset
from .forms import WithdrawForm, InvestmentForm, OwnersEquityForm, FixedAssetForm
import datetime
from Core.choices import get_prev_month, last_day_of_month, all_dates_in_month
from Transaction.models import CashBalance
    
# Withdraw
@login_required
def WithdrawFormsetView(request, date):
    qs = Withdraw.objects.filter(date=date)
    extra = 0 if qs.count() > 0 else 1
    WithdrawFormSet = modelformset_factory(Withdraw, WithdrawForm, extra=extra, can_delete=True)
    formset = WithdrawFormSet(request.POST or None, queryset=qs)
    formset.initial = [{'date':date} for i in range(0,extra)]
    empty_form = formset.empty_form
    empty_form.initial = {'date':date}
    template = "Owner/withdraw_formset.html"
    context = {
        'formset': formset, 
        'empty_form': empty_form,
        'date': date,
        }

    if request.method == 'POST':
        # if formset.errors:
        #     print(formset.errors)
        if formset.is_valid():
            formset.save()
            # instances = formset.save(commit=False)
            # for obj in formset.deleted_objects:
            #     obj.delete()
            return redirect('daily-transactions', date)
    return render(request,template,context)
    
# Owners Equity
class OwnersEquityView(LoginRequiredMixin,ListView):
    model = OwnersEquity
    template_name = 'Owner/ownersequity.html'
    paginate_by = 24

    def get(self, request, *args, **kwargs):
        if not CashBalance.objects.exists():
            return redirect('create-cashbalance')
        
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.model.objects.all().order_by('year','month')
        object_list = []
        for qs in queryset:
            month = int(qs.month)
            year = int(qs.year)
            prev_month_year, prev_month = get_prev_month(year, month)
            prev_qs = queryset.filter(month=prev_month,year=prev_month_year,owner=qs.owner)
            if prev_qs:
                prev_oe = prev_qs.last()

                cashbalances = CashBalance.objects.filter(date__month=month,date__year=year)
                if cashbalances:
                    from_date = datetime.date(year,month,1)
                    to_date = cashbalances.order_by('date').last().date
                    
                    withdraws = Withdraw.objects.filter(owner=qs.owner, date__gte=from_date, date__lte=to_date)
                    withdraw_amount = withdraws.aggregate(Sum('amount'))['amount__sum']
                    investments = Investment.objects.filter(owner=qs.owner, date__gte=from_date, date__lte=to_date)
                    investment_amount = investments.aggregate(Sum('amount'))['amount__sum']
                    obj = {
                        'month': qs.month, 
                        'year': qs.year, 
                        'owner': qs.owner,
                        'prev_oe': prev_oe.amount or 0,
                        'profit': qs.profit or 0,
                        'withdraw': withdraw_amount or 0,
                        'investment': investment_amount or 0,
                        'current_oe': qs.amount or 0,
                        'share': qs.share,
                        'prev_share': prev_oe.share
                    }
                    object_list.insert(0,obj)
        return object_list

class OwnersEquityDetailView(LoginRequiredMixin,TemplateView):
    template_name = 'Owner/ownersequity_detail.html'
    
    def get(self, request, *args, **kwargs):
        if not CashBalance.objects.exists():
            return redirect('create-cashbalance')
        
        today = datetime.date.today()
        # pk
        if 'owner' in self.request.GET:
            self.kwargs['pk'] = self.request.GET.get('owner')
        elif 'pk' not in self.kwargs:
            self.kwargs['pk'] = Owner.objects.first().pk
        # Month and year
        if 'month' in self.request.GET and 'year' in self.request.GET:
            self.kwargs['month'] = int(self.request.GET.get('month'))
            self.kwargs['year'] = int(self.request.GET.get('year'))
        elif 'month' not in self.kwargs and 'year' not in self.kwargs:
            self.kwargs['month'] = today.month
            self.kwargs['year'] = today.year

        pk = self.kwargs['pk']
        month = self.kwargs['month']
        year = self.kwargs['year']
        target_date = datetime.date(year,month,1)
        self.kwargs['target_date'] = target_date

        oe = OwnersEquity.objects.filter(owner=pk).order_by('year','month')

        if oe.count() == 0:
            context = self.get_context_data()
            return super(TemplateView, self).render_to_response(context)
        
        last_oe = oe.last()
        first_oe = oe.first()

        first_oe_date = datetime.date(int(first_oe.year),int(first_oe.month),1)
        last_oe_date = datetime.date(int(last_oe.year),int(last_oe.month),1)
        next_to_first = first_oe_date + datetime.timedelta(days=31)
        # next_to_last = last_oe_date + datetime.timedelta(days=31)
        # print(next_to_first, next_to_last)
        
        if target_date > last_oe_date:
            return redirect('ownersequity-details', 
                pk = self.kwargs['pk'], 
                month = last_oe_date.month, 
                year = last_oe_date.year)
        elif target_date < next_to_first:
            return redirect('ownersequity-details', 
                pk = self.kwargs['pk'], 
                month = next_to_first.month, 
                year = next_to_first.year)
        
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        owner = Owner.objects.get(pk=self.kwargs['pk'])
        context['owner'] = owner
        self.kwargs['owner'] = owner
        month = self.kwargs['month']
        year = self.kwargs['year']
        target_date = self.kwargs['target_date']
        prev_date = target_date - datetime.timedelta(days=1)
        next_date = target_date + datetime.timedelta(days=31)
        last_day = last_day_of_month(year,month)
        context['prev'] = prev_date
        context['next'] = next_date
        context['month'] = month
        context['year'] = year
        context["filter_form"] = OwnersEquityForm(self.kwargs or None)

        prev_oe = OwnersEquity.objects.get(owner=owner,month=prev_date.month,year=prev_date.year)
        context['prev_oe'] = prev_oe
        current_oe = OwnersEquity.objects.filter(owner=owner,month=month,year=year)
        context['current_oe'] = current_oe.last()
        investments = Investment.objects.filter(owner=owner,date__month=month,date__year=year)
        investment_amount = investments.aggregate(Sum('amount'))['amount__sum']
        context['investments'] = investments
        context['total_investment'] = investment_amount
        withdraws = Withdraw.objects.filter(owner=owner,date__month=month,date__year=year)
        withdraw_amount = withdraws.aggregate(Sum('amount'))['amount__sum']
        wd_data = []
        dates = all_dates_in_month(year,month)
        for date in dates:
            wds = withdraws.filter(date=date)
            if wds:
                data = {}
                # for wd in wds:
                #     data['detail'] = wd.detail
                #     data['amount'] = wd.amount
                wd_total = wds.aggregate(Sum('amount'))['amount__sum']
                wd_data.append({
                    'date': date,
                    'wds': wds,
                    'total': wd_total
                })

        context['withdraws'] = wd_data
        context['wd_rowspan'] = len(wd_data)
        context['total_withdraw'] = withdraw_amount
        return context
    
class InvestmentCreateView(LoginRequiredMixin,CreateView):
    model = Investment
    form_class = InvestmentForm
    template_name = 'Owner/investment_form.html'

# class InvestmentUpdateView(UpdateView):
#     model = Investment
#     form_class = InvestmentForm

class InvestmentDeleteView(LoginRequiredMixin,DeleteView):
    model = Investment
    success_url = reverse_lazy('daily-transactions')

class FixedAssetView(LoginRequiredMixin,CreateView, ListView):
    model = FixedAsset
    form_class = FixedAssetForm
    template_name = 'Owner/fixedassets.html'

class FixedAssetDeleteView(LoginRequiredMixin,DeleteView):
    model = FixedAsset
    success_url = reverse_lazy('fixed-assets')