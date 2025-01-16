from django.views.generic import TemplateView
from django.db.models import Sum


# class ProfitAdjustment(RedirectMixin, TemplateView):
#     template_name = 'Ledger/profit_adjustment.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         month = self.kwargs['month']
#         year = self.kwargs['year']
#         context['month'] = month
#         context['year'] = year
#         last_bal_date = CashBalance.objects.latest().date
#         context['last_bal_date'] = last_bal_date
#         to_date = last_day_of_month(year,month)
#         if last_bal_date <= to_date: context['status'] = True
#         product_info, total_profit, total_profit_diff = get_products_info(year,month)
#         context['product_info'] = product_info
#         context['total_profit_diff'] = total_profit_diff
#         return context
    