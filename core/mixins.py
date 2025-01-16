import datetime
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.conf import settings

from Transaction.models import CashBalance
from Transaction.functions import last_balance_date, last_balance_date_of_month

from Core.models import Settings
from Core.forms import DateForm
from Core.functions import first_date_of_month, last_date_of_month, account_start_date, next_day, prev_day, prev_month, next_month

class RedirectMixin(LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        current_url = request.path
        settings = Settings.objects.first()
        print(settings)
        
        if not settings:
            if current_url != reverse('create-settings'):
                return redirect('create-settings')
        elif not CashBalance.objects.exists():
            if current_url != reverse('update-settings', kwargs={'pk': settings.pk}):
                start_date = settings.start_date
                if current_url != reverse('create-cashbalance', kwargs={'date': start_date}):
                    return redirect(reverse('create-cashbalance', kwargs={'date': start_date}))

        return super().get(request, *args, **self.kwargs)


class NavigationMixin(RedirectMixin,View):
    date = last_balance_date()
    """
    This is used to perfectly navigate to months based on Cashbalance.
    """

    def get_url_name(self, request):
        url_name = request.resolver_match.url_name if request.resolver_match else None
        return url_name
    
    def get_navigation(self):
        self.prev_day = datetime.datetime.strftime(prev_day(self.date),settings.DATE_FORMAT)
        self.next_day = datetime.datetime.strftime(next_day(self.date),settings.DATE_FORMAT)

    def get(self, request, *args, **kwargs):
        # Set month and year from GET request
        if 'date_day' in self.request.GET:
            try:
                self.date = datetime.date(
                    int(self.request.GET.get('date_year')),
                    int(self.request.GET.get('date_month')),
                    int(self.request.GET.get('date_day'))
                )
            except ValueError: 
                temp_date = datetime.date(
                    int(self.request.GET.get('date_year')),
                    int(self.request.GET.get('date_month')),
                    1
                )
                self.date = last_balance_date_of_month(temp_date)
            self.kwargs['date'] = self.date
            return redirect(reverse(self.get_url_name(request),kwargs=self.kwargs))
        elif 'date' in kwargs:
            self.date = self.kwargs['date']
        request.META['navigation_date'] = self.date
        
        self.get_navigation()
        self.from_date = first_date_of_month(self.date)

        # Handle cases where the target date is outside allowed ranges
        current_day = last_balance_date()
        start_date = account_start_date()
        if self.date > current_day:
            self.kwargs['date'] = current_day
            return redirect(reverse(self.get_url_name(request),kwargs=self.kwargs))
        elif self.date < start_date:
            self.kwargs['date'] = start_date
            return redirect(reverse(self.get_url_name(request),kwargs=self.kwargs))

        # Proceed to the standard get process of the parent class
        return super().get(request, *args, **self.kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_day = last_date_of_month(self.date)
        context['status'] = last_day == self.date
        context['date'] = self.date
        # Navigation
        pattern_name = self.get_url_name(self.request)
        self.get_navigation()
        # Day wise
        prev_day_kwargs = self.kwargs.copy()
        next_day_kwargs = self.kwargs.copy()
        prev_day_kwargs['date'] = self.prev_day
        next_day_kwargs['date'] = self.next_day
        context['prev_day_url'] = reverse(pattern_name,kwargs=prev_day_kwargs)
        context['next_day_url'] = reverse(pattern_name,kwargs=next_day_kwargs)
        # Month wise
        prev_month_kwargs = self.kwargs.copy()
        next_month_kwargs = self.kwargs.copy()
        last_date = last_balance_date_of_month(self.date)
        prev_month_kwargs['date'] = last_date_of_month(prev_month(self.date))
        if self.date != last_date:
            next_month_kwargs['date'] = last_date
        else:
            next_month_kwargs['date'] = last_balance_date_of_month(next_month(self.date))
        
        context['prev_month_url'] = reverse(pattern_name,kwargs=prev_month_kwargs)
        context['next_month_url'] = reverse(pattern_name,kwargs=next_month_kwargs)
        
        context['filter_form'] = DateForm(initial={'date':self.date})
        return context
    
    def get_filter_object_name():
        return None