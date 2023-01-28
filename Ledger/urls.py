from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views.main import LedgerList, saveLedger, RevenueLedger, ExpenditureLedger, WithdrawLedger
from .views.customer_views import (
    CustomerLedger, GroupofCompanyLedger,
    CustomerBalanceView, deleteCustomerBalance,
    GroupofCompanyBalanceView, deleteGroupofCompanyBalance,
)
from .views.product_views import StorageView, ProductLedger

urlpatterns = [
    path('', LedgerList.as_view(), name='ledger-list'),
    path('<int:month>-<int:year>/', LedgerList.as_view(), name='ledger-list'),
    path('<date:date>/save/', saveLedger, name='save-ledger'),
    path('customer/', include([
        path('<int:pk>/', CustomerLedger.as_view(), name='customer-ledger'),
        path('<int:pk>/<int:month>-<int:year>/', CustomerLedger.as_view(), name='customer-ledger'),
        path('balance/', include([
            path('', CustomerBalanceView.as_view(), name='customer-balance'),
            path('<int:cust_id>/', CustomerBalanceView.as_view(), name='customer-balance'),
            path('<int:pk>/delete/', deleteCustomerBalance, name='delete-customer-balance'),
        ])),
    ])),
    path('groupofcompany/', include([
        path('<int:pk>/', GroupofCompanyLedger.as_view(), name='groupofcompany-ledger'),
        path('<int:pk>/<int:month>-<int:year>/', GroupofCompanyLedger.as_view(), name='groupofcompany-ledger'),
        path('balance/', include([
            path('', GroupofCompanyBalanceView.as_view(), name='groupofcompany-balance'),
            path('<int:cust_id>/', GroupofCompanyBalanceView.as_view(), name='groupofcompany-balance'),
            path('<int:pk>/delete/', deleteGroupofCompanyBalance, name='delete-groupofcompany-balance'),
        ])),
    ])),
    path('product/', include([
        path('storage/', StorageView.as_view(), name='product-storage'),
        path('storage/<int:product_id>/', StorageView.as_view(), name='product-storage'),
        path('storage/<int:product_id>/<int:month>-<int:year>/', StorageView.as_view(), name='product-storage'),
        path('ledger/',include([
            path('<int:pk>', ProductLedger.as_view(), name='product-ledger'),
            path('<int:pk>/<int:month>-<int:year>/', ProductLedger.as_view(), name='product-ledger'),
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
]
