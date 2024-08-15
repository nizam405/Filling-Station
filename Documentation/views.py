from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class DocumentationHome(LoginRequiredMixin, TemplateView):
    template_name = 'Documentation/home.html'

class GetStarted(LoginRequiredMixin, TemplateView):
    template_name = 'Documentation/get_started.html'

class ProductManagement(LoginRequiredMixin, TemplateView):
    template_name = 'Documentation/product_management.html'

class ExpRev(LoginRequiredMixin, TemplateView):
    template_name = 'Documentation/exp_rev.html'

class Party(LoginRequiredMixin, TemplateView):
    template_name = 'Documentation/party.html'

class DailyTransaction(LoginRequiredMixin, TemplateView):
    template_name = 'Documentation/daily_transaction.html'

class Ledger(LoginRequiredMixin, TemplateView):
    template_name = 'Documentation/ledger.html'

class IncomeStatement(LoginRequiredMixin, TemplateView):
    template_name = 'Documentation/income_statement.html'

class OE(LoginRequiredMixin, TemplateView):
    template_name = 'Documentation/oe.html'

class Loan(LoginRequiredMixin, TemplateView):
    template_name = 'Documentation/loan.html'

class ErrorHandling(LoginRequiredMixin, TemplateView):
    template_name = 'Documentation/error_handling.html'