from django.urls import path, include
from .views import (
    DocumentationHome, GetStarted, ProductManagement, ExpRev, Party, DailyTransaction, Ledger, IncomeStatement, OE, Loan, ErrorHandling
    )

urlpatterns = [
    path('', DocumentationHome.as_view(), name='doc-home'),
    path('get-started/', GetStarted.as_view(), name='doc-get-started'),
    path('product-management/', ProductManagement.as_view(), name='doc-product-management'),
    path('exp-rev/', ExpRev.as_view(), name='doc-exp-rev'),
    path('party/', Party.as_view(), name='doc-party'),
    path('daily-transaction/', DailyTransaction.as_view(), name='doc-daily-transaction'),
    path('ledger/', Ledger.as_view(), name='doc-ledger'),
    path('income-statement/', IncomeStatement.as_view(), name='doc-income-statement'),
    path('oe/', OE.as_view(), name='doc-oe'),
    path('loan/', Loan.as_view(), name='doc-loan'),
    path('error-handling/', ErrorHandling.as_view(), name='doc-error-handling'),
]
