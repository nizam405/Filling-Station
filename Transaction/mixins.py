from django.shortcuts import redirect
from Transaction.models import CashBalance

class BalanceRequiredMixin:
    def get(self, request, *args, **kwargs):
        if not CashBalance.objects.exists():
            return redirect('daily-transactions')

        # Proceed to the standard get process of the parent class
        return super().get(request, *args, **self.kwargs)