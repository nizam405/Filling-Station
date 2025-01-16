from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import dues, goc, customer, ledger

urlpatterns = [
    # Group of Company
    path('groupofcompany/', include([
        path('list/', goc.GroupofCompaniesView.as_view(), name="groupofcompanies"),
        path('<int:pk>/', include([
            path('update/',  goc.GroupofCompanyUpdateView.as_view(), name="update-groupofcompany"),
            path('delete/',  goc.GroupofCompanyDeleteView.as_view(), name="delete-groupofcompany"),
            path('status/',  goc.change_goc_status, name="change-goc-status"),
            path('dues/', include([
                # 
            ])),
            path('<date:date>/<int:goc>/mark-baddebt/', dues.markBaddebt, name='mark-baddebt'),
            path('<date:date>/<int:goc>/<int:unmark>/unmark-baddebt/', dues.markBaddebt, name='mark-baddebt'),
        ])),
    ])),

    # Customer
    path('', include([
        path('list/',  customer.CustomerView.as_view(), name="customers"),
        path('<int:pk>/', include([
            path('update/',  customer.CustomerUpdateView.as_view(), name="update-customer"),
            path('delete/',  customer.CustomerDeleteView.as_view(), name="delete-customer"),
            path('status/',  customer.change_cust_status, name="change-cust-status"),
            path('<date:date>/mark-baddebt/', dues.markBaddebt, name='mark-baddebt'),
            path('<date:date>/<int:unmark>/unmark-baddebt/', dues.markBaddebt, name='mark-baddebt'),
        ])),
        path('dues/<date:date>/', include([
            path('', dues.CustomerDueView.as_view(), name='customer-due'),
            path('update/', dues.customerBalanceFormsetView, name='customer-due-update'),
        ])),
    ])),

    # Due Collection
    path('duecollection/<date:date>/', include([
        path('create/', dues.DueCollectionCreateView.as_view(), name="create-duecollection"),
        path('<int:pk>/', include([
            path('update/', dues.DueCollectionUpdateView.as_view(), name='update-duecollection'),
            path('delete/', dues.DueCollectionDeleteView.as_view(), name='delete-duecollection'),
        ])),
    ])),

    # Due Sell
    path('duesell/<date:date>/',  include([
        path('create/', dues.DueSellCreateView.as_view(), name="create-duesell"),
        path('<int:pk>/update/', dues.DueSellUpdateView.as_view(), name="update-duesell"),
        path('<int:pk>/delete/', dues.DueSellDeleteView.as_view(), name="delete-duesell"),
    ])),

    # Ledger
    path('ledger/', include([
        path('<date:date>/', include([
            path('topsheet/', ledger.CustomerTopSheet.as_view(), name='customer-topsheet'),
            path('customer/<int:customer>/', ledger.CustomerLedger.as_view(), name='customer-ledger'),
            path('goc/<int:customer>/', ledger.GroupofCompanyLedger.as_view(), name='groupofcompany-ledger'),
        ])),
    ])),
]