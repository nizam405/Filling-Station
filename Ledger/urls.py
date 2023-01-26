from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views.main import LedgerList
from .views.customer_views import (
    CustomerLedger, GroupofCompanyLedger,
    CustomerBalanceView, deleteCustomerBalance,
    GroupofCompanyBalanceView, deleteGroupofCompanyBalance,
)
from .views.product_views import StorageView

urlpatterns = [
    path('', LedgerList.as_view(), name='ledger-list'),
    path('<int:month>-<int:year>/', LedgerList.as_view(), name='ledger-list'),
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
    path('product', include([
        path('storage/', StorageView.as_view(), name='product-storage'),
        path('storage/<int:product_id>', StorageView.as_view(), name='product-storage'),
    ])),
]
