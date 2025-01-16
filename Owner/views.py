from typing import Any
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.db.models import Sum

from .models import Owner, Withdraw, Investment, OwnersEquity, FixedAsset
from .forms import WithdrawFilterForm, OwnersEquityDetailFilter, FixedAssetForm, OwnersEquityFilter
from Core.mixins import RedirectMixin, NavigationMixin
from Transaction.functions import last_balance_date
    
# Withdraw
class BaseWithdrawView(RedirectMixin, ListView):
    model = Withdraw
    fields = ['owner','detail','amount']
    template_name = 'Owner/withdraw.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = self.kwargs['date']
        qs = self.get_queryset()
        context['total'] = qs.aggregate(Sum('amount'))['amount__sum'] if qs else 0
        return context
    
    def get_queryset(self):
        return self.model.objects.filter(date=self.kwargs['date'])

class WithdrawCreateView(CreateView, BaseWithdrawView): pass
class WithdrawUpdateView(UpdateView, BaseWithdrawView): pass

class WithdrawDeleteView(RedirectMixin, DeleteView):
    model = Withdraw

    def get(self, request, *args, **kwargs):
        self.delete(request)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('create-withdraw', kwargs={'date':self.kwargs['date']})

class WithdrawLedgerView(NavigationMixin, ListView):
    model = Withdraw
    template_name = 'Owner/withdraw_ledger.html'

    def get(self,request,*args, **kwargs):
        if 'owner' in self.request.GET:
            self.owner = Owner.objects.get(pk=self.request.GET.get('owner'))
        elif 'owner' in self.kwargs:
            self.owner = Owner.objects.get(pk=self.kwargs['owner'])
        else: self.owner = Owner.objects.first()
        self.kwargs['owner'] = self.owner.pk
        return super().get(request,*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = WithdrawFilterForm(
            initial={'date':self.date,'owner':self.owner}
        )
        context['owner'] = self.owner
        qs = self.get_queryset()
        context['total'] = qs.aggregate(Sum('amount'))['amount__sum'] if qs else 0
        return context
    
    def get_queryset(self):
        return self.model.objects.filter(
            date__gte = self.from_date,
            date__lte = self.date,
            owner = self.owner
        )
    
# Owners Equity
class OwnersEquityView(RedirectMixin, ListView):
    model = OwnersEquity
    template_name = 'Owner/ownersequity.html'
    # paginate_by = 24

    def get_queryset(self):
        self.year = self.request.GET.get('year', last_balance_date().year)
        queryset = self.model.objects.filter(date__year=self.year)
        if 'owner' in self.request.GET:
            owner = self.request.GET.get('owner')
            if owner: queryset = queryset.filter(owner__id=owner)
        self.queryset = queryset
        return queryset
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = OwnersEquityFilter(
            self.request.GET or None,
            initial = {'year': last_balance_date().year}
        )
        context['year'] = self.year
        qs = self.get_queryset()

        yearly = {
            'initial'   : qs.earliest().amount or 0, 
            'profit'    : qs.aggregate(Sum('profit'))['profit__sum']    or 0,
            'withdraw'  : sum(obj.withdraw['amount'] for obj in qs)     or 0,
            'investment': sum(obj.investment['amount'] for obj in qs)   or 0,
            'ending'    : 0
        }

        # total['remaining'] = total['profit']+total['investment']-total['withdraw']
        context['yearly'] = yearly
        return context

class OwnersEquityDetailView(NavigationMixin, TemplateView):
    template_name = 'Owner/ownersequity_detail.html'
    model = OwnersEquity
    
    def get(self,request,*args, **kwargs):
        if 'owner' in self.request.GET:
            self.owner = Owner.objects.get(pk=self.request.GET.get('owner'))
        elif 'owner' in self.kwargs:
            self.owner = Owner.objects.get(pk=self.kwargs['owner'])
        else: self.owner = Owner.objects.first()
        self.kwargs['owner'] = self.owner.pk
        return super().get(request,*args, **kwargs)
    
    def get_queryset(self):
        return self.model.objects.get(
            owner=self.owner,
            date__gte=self.from_date,
            date__lte=self.date
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_queryset()
        context["filter_form"] = OwnersEquityDetailFilter({'owner':self.owner,'date':self.date})
        return context
    
class BaseInvestmentView(RedirectMixin, ListView):
    model = Investment
    fields = ['owner', 'detail', 'amount']
    template_name = 'Owner/investment_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = self.kwargs['date']
        qs = self.get_queryset()
        context['total'] = qs.aggregate(Sum('amount'))['amount__sum'] if qs else 0
        return context
    
    def get_queryset(self):
        return self.model.objects.filter(date=self.kwargs['date'])
    
class InvestmentCreateView(CreateView, BaseInvestmentView):pass
class InvestmentUpdateView(UpdateView, BaseInvestmentView):pass

class InvestmentDeleteView(RedirectMixin, DeleteView):
    model = Investment

    def get(self, request, *args, **kwargs):
        self.delete(request)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('create-investment', kwargs={'date':self.kwargs['date']})

class FixedAssetView(RedirectMixin, CreateView, ListView):
    model = FixedAsset
    form_class = FixedAssetForm
    template_name = 'Owner/fixedassets.html'

class FixedAssetDeleteView(RedirectMixin, DeleteView):
    model = FixedAsset
    success_url = reverse_lazy('fixed-assets')