from django.urls import path

from .views import (
    CustomerListView, CustomerDetailView,
    CustomerCreateView, CustomerUpdateView, CustomerDeleteView,
    DueCollectionListView, DueCollectionCreateView, DueCollectionUpdateView, DueCollectionDeleteView,
    DueSellListView, DueSellCreateView, DueSellUpdateView, DueSellDeleteView
)

urlpatterns = [
    # Customer
    path('list/', CustomerListView.as_view(), name="customer-list"),
    path('<int:pk>/detail/', CustomerDetailView.as_view(), name="customer-detail"),
    path('create/', CustomerCreateView.as_view(), name="create-customer"),
    path('<int:pk>/update/', CustomerUpdateView.as_view(), name="update-customer"),
    path('<int:pk>/delete/', CustomerDeleteView.as_view(), name="delete-customer"),

    # Due Collection
    path('duecollection/list/', DueCollectionListView.as_view(), name="duecollection-list"),
    path('duecollection/create/', DueCollectionCreateView.as_view(), name="create-duecollection"),
    path('duecollection/<int:pk>/update/', DueCollectionUpdateView.as_view(), name="update-duecollection"),
    path('duecollection/<int:pk>/delete/', DueCollectionDeleteView.as_view(), name="delete-duecollection"),

    # Customer Due
    path('duesell/list/', DueSellListView.as_view(), name="duesell-list"),
    path('duesell/create/', DueSellCreateView.as_view(), name="create-duesell"),
    path('duesell/<int:pk>/update/', DueSellUpdateView.as_view(), name="update-duesell"),
    path('duesell/<int:pk>/delete/', DueSellDeleteView.as_view(), name="delete-duesell"),
]