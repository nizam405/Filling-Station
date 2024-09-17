from django.shortcuts import redirect
from Transaction.models import CashBalance
from Ledger.forms import DateFilterForm
from Transaction.functions import (first_balance_date, last_balance_date, first_ledger_month_date)
from Core.choices import first_date_of_month
from Ledger.functions import get_navigation_context

class LedgerTopSheetMixin:
    """
    This is used to perfectly navigate to months based on Cashbalance.
    """
    # Default redirect URL name if none is dynamically determined
    default_url_name = 'daily-transactions'

    def get_url_name(self, request):
        """
        Returns the URL name to redirect to when the CashBalance check fails.
        This method tries to dynamically determine the current view's URL name
        or falls back to a default URL name if none is found.
        """
        if CashBalance.objects.exists():
            # Attempt to get the current URL pattern name
            current_url_name = request.resolver_match.url_name if request.resolver_match else None
            return current_url_name
        else: return self.default_url_name

    def get(self, request, *args, **kwargs):
        # Redirect if no CashBalance records exist
        if not CashBalance.objects.exists():
            print('cashbalance not exists')
            return redirect(self.get_url_name(request))

        # Get first and last CashBalance dates
        first_bal_date = first_balance_date()
        last_bal_date = last_balance_date()

        # Calculate the first date of the first month and adjust it
        first_ledger_date = first_ledger_month_date()

        # Set month and year from GET request or default to last_bal_date
        if 'month' in request.GET and 'year' in request.GET:
            self.kwargs['month'] = int(request.GET['month'])
            self.kwargs['year'] = int(request.GET['year'])
        elif 'month' not in kwargs and 'year' not in kwargs:
            self.kwargs['month'] = last_bal_date.month
            self.kwargs['year'] = last_bal_date.year

        # Set the target date based on the month and year
        month = self.kwargs['month']
        year = self.kwargs['year']
        target_date = first_date_of_month(year, month)

        # Handle cases where the target date is outside allowed ranges
        if last_bal_date.year == first_bal_date.year and last_bal_date.month == first_bal_date.month:
            target_date = last_bal_date
        print(target_date, first_bal_date, last_bal_date)
        if target_date > last_bal_date:
            return redirect(self.get_url_name(request), month=last_bal_date.month, year=last_bal_date.year)
        elif target_date < first_bal_date:
            return redirect(self.get_url_name(request), month=first_ledger_date.month, year=first_ledger_date.year)

        # Proceed to the standard get process of the parent class
        return super().get(request, *args, **self.kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date_form'] = DateFilterForm(self.request.GET or self.kwargs or None)
        
        # Ensure required keys are present in kwargs
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        context.update(get_navigation_context(year,month))
        return context
        