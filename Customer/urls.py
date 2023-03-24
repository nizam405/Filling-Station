from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    GroupofCompaniesView, GroupofCompanyUpdateView, GroupofCompanyDeleteView, change_goc_status,
    CustomerView, CustomerUpdateView, CustomerDeleteView, change_cust_status,
    DueCollectionFormsetView, DueSellFormsetView,
)

urlpatterns = [
    # Group of Company
    path('groupofcompany/', include([
        path('list/', GroupofCompaniesView.as_view(), name="groupofcompanies"),
        path('<int:pk>/update/', GroupofCompanyUpdateView.as_view(), name="update-groupofcompany"),
        path('<int:pk>/delete/', GroupofCompanyDeleteView.as_view(), name="delete-groupofcompany"),
        path('<int:pk>/status/', change_goc_status, name="change-goc-status"),
    ])),

    # Customer
    path('', include([
        path('list/', CustomerView.as_view(), name="customers"),
        path('<int:pk>/update/', CustomerUpdateView.as_view(), name="update-customer"),
        path('<int:pk>/delete/', CustomerDeleteView.as_view(), name="delete-customer"),
        path('<int:pk>/status/', change_cust_status, name="change-cust-status"),
    ])),

    # Dues
    path('duecollection/<date:date>/', DueCollectionFormsetView, name="duecollection"),
    path('duesell/<date:date>/', DueSellFormsetView, name="duesell"),
]