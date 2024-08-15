from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views.main import RevenueLedger, ExpenditureLedger, WithdrawLedger
from .views.customer_views import (
    CustomerTopSheet,
    CustomerLedger, GroupofCompanyLedger,
    CustomerBalanceView, customerBalanceFormsetView, markBaddebt,
)
from .views.product_views import StorageView, ProductLedger, ProductTopSheet, storage_formset_view
from .views.incomestatement_view import IncomeStatementView, ProfitAdjustment

urlpatterns = [
    path('customer/', include([
        path('topsheet/', include([
            path('', CustomerTopSheet.as_view(), name='customer-topsheet'),
            path('<int:month>-<int:year>/', CustomerTopSheet.as_view(), name='customer-topsheet'),
        ])),
        path('', include([
            path('', CustomerLedger.as_view(), name='customer-ledger'),
            path('<int:customer>/', CustomerLedger.as_view(), name='customer-ledger'),
            path('<int:customer>/<int:month>-<int:year>/', CustomerLedger.as_view(), name='customer-ledger'),
        ])),
        path('balance/', include([
            path('', CustomerBalanceView.as_view(), name='customer-balance'),
            path('<int:month>-<int:year>/', CustomerBalanceView.as_view(), name='customer-balance'),
            path('update/<int:month>-<int:year>/', customerBalanceFormsetView, name='customer-balance-update'),
            # Bad Debts
            path('<int:month>-<int:year>/<int:cust_pk>/mark-baddebt/', markBaddebt, name='mark-baddebt'),
            path('<int:month>-<int:year>/<int:goc>/<int:cust_pk>/mark-baddebt/', markBaddebt, name='mark-baddebt'),
            path('<int:month>-<int:year>/<int:cust_pk>/<int:unmark>/unmark-baddebt/', markBaddebt, name='mark-baddebt'),
            path('<int:month>-<int:year>/<int:goc>/<int:cust_pk>/<int:unmark>/unmark-baddebt/', markBaddebt, name='mark-baddebt'),
        ])),
    ])),
    path('groupofcompany/', include([
        path('', include([
            path('', GroupofCompanyLedger.as_view(), name='groupofcompany-ledger'),
            path('<int:customer>/', GroupofCompanyLedger.as_view(), name='groupofcompany-ledger'),
            path('<int:customer>/<int:month>-<int:year>/', GroupofCompanyLedger.as_view(), name='groupofcompany-ledger'),
        ])),
    ])),
    path('product/', include([
        path('topsheet/', include([
            path('', ProductTopSheet.as_view(), name='product-topsheet'),
            path('<int:month>-<int:year>/', ProductTopSheet.as_view(), name='product-topsheet'),
        ])),
        path('',include([
            path('', ProductLedger.as_view(), name='product-ledger'),
            path('<int:pk>', ProductLedger.as_view(), name='product-ledger'),
            path('<int:pk>/<int:month>-<int:year>/', ProductLedger.as_view(), name='product-ledger'),
        ])),
        path('storage/', include([
            path('', StorageView.as_view(), name='product-storage'),
            path('<int:month>-<int:year>/', StorageView.as_view(), name='product-storage'),
            path('update/<int:month>-<int:year>/', storage_formset_view, name='update-product-storage'),
        ])),
    ])),
    path('revenue/', include([
        path('', RevenueLedger.as_view(), name='revenue-ledger'),
        path('<int:month>-<int:year>/', RevenueLedger.as_view(), name='revenue-ledger'),
    ])),
    path('expenditure/', include([
        path('', ExpenditureLedger.as_view(), name='expenditure-ledger'),
        path('<int:month>-<int:year>/', ExpenditureLedger.as_view(), name='expenditure-ledger'),
    ])),
    path('withdraw/', include([
        path('', WithdrawLedger.as_view(), name='withdraw-ledger'),
        path('<int:month>-<int:year>/', WithdrawLedger.as_view(), name='withdraw-ledger'),
    ])),
    # path('<date:date>/save/', saveLedger, name='save-ledger'),
    path('incomestatement/', include([
        path('', IncomeStatementView.as_view(), name='incomestatement'),
        path('<int:month>-<int:year>/', IncomeStatementView.as_view(), name='incomestatement'),
    ])),
    path('profit-adjustment/<int:month>-<int:year>/', ProfitAdjustment.as_view(), name='profit-adjustment'),
]
