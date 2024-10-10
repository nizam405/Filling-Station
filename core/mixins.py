from django.shortcuts import redirect
from django.urls import reverse
from Transaction.models import CashBalance, DailyBalance
from Core.models import Settings
from django.contrib.auth.mixins import LoginRequiredMixin

class RedirectMixin(LoginRequiredMixin):
    def get(self, request, *args, **kwargs):
        current_url = request.path
        if not Settings.objects.exists():
            if current_url != reverse('create-settings'):
                return redirect('create-settings')
        elif not DailyBalance.objects.exists():
            if current_url != reverse('create-dailybalance'):
                return redirect('create-dailybalance')
        # else: 
        #     if current_url != reverse('daily-transactions'):
        #         return redirect('daily-transactions')

        # Proceed to the standard get process of the parent class
        return super().get(request, *args, **self.kwargs)