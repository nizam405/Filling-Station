from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views.main import saveLedger, RevenueLedger, ExpenditureLedger, WithdrawLedger
from .views.customer_views import (
    CustomerTopSheet,
    CustomerLedger, GroupofCompanyLedger,
    CustomerBalanceView, deleteCustomerBalance,
    GroupofCompanyBalanceView, deleteGroupofCompanyBalance,
    BadDebtView, deleteBadDebt,
)
from .views.product_views import StorageView, ProductLedger, ProductTopSheet
from .views.incomestatement_view import IncomeStatementView

urlpatterns = [
    path('customer/', include([
        path('topsheet/', include([
            path('', CustomerTopSheet.as_view(), name='customer-topsheet'),
            path('<int:month>-<int:year>/', CustomerTopSheet.as_view(), name='customer-topsheet'),
        ])),
        path('bad-debt/', include([
            path('', BadDebtView.as_view(), name='baddebt'),
            path('<int:pk>/delete', deleteBadDebt, name='delete-baddebt'),
        ])),
        path('', include([
            path('', CustomerLedger.as_view(), name='customer-ledger'),
            path('<int:customer>/', CustomerLedger.as_view(), name='customer-ledger'),
            path('<int:customer>/<int:month>-<int:year>/', CustomerLedger.as_view(), name='customer-ledger'),
        ])),
        path('balance/', include([
            path('', CustomerBalanceView.as_view(), name='customer-balance'),
            path('<int:cust_id>/', CustomerBalanceView.as_view(), name='customer-balance'),
            path('<int:month>-<int:year>/', CustomerBalanceView.as_view(), name='customer-balance'),
            path('<int:pk>/delete/', deleteCustomerBalance, name='delete-customer-balance'),
        ])),
    ])),
    path('groupofcompany/', include([
        path('', include([
            path('', GroupofCompanyLedger.as_view(), name='groupofcompany-ledger'),
            path('<int:customer>/', GroupofCompanyLedger.as_view(), name='groupofcompany-ledger'),
            path('<int:customer>/<int:month>-<int:year>/', GroupofCompanyLedger.as_view(), name='groupofcompany-ledger'),
        ])),
        path('balance/', include([
            path('', GroupofCompanyBalanceView.as_view(), name='groupofcompany-balance'),
            path('<int:cust_id>/', GroupofCompanyBalanceView.as_view(), name='groupofcompany-balance'),
            path('<int:month>-<int:year>/', GroupofCompanyBalanceView.as_view(), name='groupofcompany-balance'),
            path('<int:pk>/delete/', deleteGroupofCompanyBalance, name='delete-groupofcompany-balance'),
        ])),
    ])),
    path('product/', include([
        path('topsheet', include([
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
            path('<int:product_id>/', StorageView.as_view(), name='product-storage'),
            path('<int:product_id>/<int:month>-<int:year>/', StorageView.as_view(), name='product-storage'),
            path('<int:month>-<int:year>/', StorageView.as_view(), name='product-storage'),
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
    path('<date:date>/save/', saveLedger, name='save-ledger'),
    path('incomestatement/', include([
        path('', IncomeStatementView.as_view(), name='incomestatement'),
        path('<int:month>-<int:year>/', IncomeStatementView.as_view(), name='incomestatement'),
    ])),
]
