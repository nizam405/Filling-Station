from django.urls import path, register_converter
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    GroupofCompaniesView, GroupofCompanyUpdateView, GroupofCompanyDeleteView,
    CustomerView, CustomerUpdateView, CustomerDeleteView,
    DueCollectionFormsetView, DueSellFormsetView,
)

urlpatterns = [
    # Group of Company
    path('groupofcompanies/', GroupofCompaniesView.as_view(), name="groupofcompanies"),
    path('groupofcompany/<int:pk>/update/', GroupofCompanyUpdateView.as_view(), name="update-groupofcompany"),
    path('groupofcompany/<int:pk>/delete/', GroupofCompanyDeleteView.as_view(), name="delete-groupofcompany"),

    # Customer
    path('', CustomerView.as_view(), name="customers"),
    path('<int:pk>/update/', CustomerUpdateView.as_view(), name="update-customer"),
    path('<int:pk>/delete/', CustomerDeleteView.as_view(), name="delete-customer"),

    # Dues
    path('duecollection/<date:date>/', DueCollectionFormsetView, name="duecollection"),
    path('duesell/<date:date>/', DueSellFormsetView, name="duesell"),
]