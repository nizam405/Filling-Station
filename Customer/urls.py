from django.urls import path, register_converter
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    GroupofCompaniesView, GroupofCompanyUpdateView, GroupofCompanyDeleteView,
    CustomerView, CustomerUpdateView, CustomerDeleteView,
    DueCollectionListView, DueCollectionCreateView, DueCollectionUpdateView, DueCollectionDeleteView,
    MultiDueCollectionCreateView,
    DueSellListView, DueSellCreateView, DueSellUpdateView, DueSellDeleteView, MultiDueSellCreateView,
)

urlpatterns = [
    # Group of Company
    path('groupofcompanies/', GroupofCompaniesView.as_view(), name="groupofcompanies"),
    # path('groupofcompany/list/', GroupofCompanyListView.as_view(), name="groupofcompany-list"),
    # path('groupofcompany/create/', GroupofCompanyCreateView.as_view(), name="create-groupofcompany"),
    path('groupofcompany/<int:pk>/update/', GroupofCompanyUpdateView.as_view(), name="update-groupofcompany"),
    path('groupofcompany/<int:pk>/delete/', GroupofCompanyDeleteView.as_view(), name="delete-groupofcompany"),

    # Customer
    path('', CustomerView.as_view(), name="customers"),
    # path('list/', CustomerListView.as_view(), name="customer-list"),
    # path('<int:pk>/detail/', CustomerDetailView.as_view(), name="customer-detail"),
    # path('create/', CustomerCreateView.as_view(), name="create-customer"),
    path('<int:pk>/update/', CustomerUpdateView.as_view(), name="update-customer"),
    path('<int:pk>/delete/', CustomerDeleteView.as_view(), name="delete-customer"),

    # Due Collection
    # path('duecollection/list/', DueCollectionListView.as_view(), name="duecollection-list"),
    path('duecollection/create/', DueCollectionCreateView.as_view(), name="create-duecollection"),
    path('duecollection/create/<date:date>/', DueCollectionCreateView.as_view(), name="create-duecollection"),
    path('duecollection/create/multi/<date:date>/', MultiDueCollectionCreateView, name="create-duecollection-multi"),
    path('duecollection/<int:pk>/update/', DueCollectionUpdateView.as_view(), name="update-duecollection"),
    path('duecollection/<int:pk>/delete/', DueCollectionDeleteView.as_view(), name="delete-duecollection"),

    # Due Sell
    # path('duesell/list/', DueSellListView.as_view(), name="duesell-list"),
    path('duesell/create/', DueSellCreateView.as_view(), name="create-duesell"),
    path('duesell/create/<date:date>/', DueSellCreateView.as_view(), name="create-duesell"),
    path('duesell/create/multi/<date:date>/', MultiDueSellCreateView, name="create-duesell-multi"),
    path('duesell/<int:pk>/update/', DueSellUpdateView.as_view(), name="update-duesell"),
    path('duesell/<int:pk>/delete/', DueSellDeleteView.as_view(), name="delete-duesell"),
]