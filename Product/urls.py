from django.urls import path, register_converter
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    ProductView, ProductUpdateView, ProductDeleteView,
    SellUpdateView, SellDeleteView, MultiSellCreateView,
    PurchaseUpdateView, PurchaseDeleteView, MultiPurchaseCreateView,
    
    )

urlpatterns = [
    # Product
    path('', ProductView.as_view(), name='products'),
    # path('product/new/', ProductCreateView.as_view(), name="create-product"),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name="update-product"),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='delete-product'),
    
    # Purchase
    # path('purchases/', PurchaseListView.as_view(), name='purchases'),
    # path('purchase/new/', PurchaseCreateView.as_view(), name="create-purchase"),
    # path('purchase/new/<date:date>/', PurchaseCreateView.as_view(), name="create-purchase"),
    path('purchase/new/multi/<date:date>/', MultiPurchaseCreateView, name="create-purchase-multi"),
    path('purchase/<int:pk>/update/', PurchaseUpdateView.as_view(), name="update-purchase"),
    path('purchase/<int:pk>/delete/', PurchaseDeleteView.as_view(), name='delete-purchase'),
    
    # Sells
    # path('sells/', SellListView.as_view(), name='sells'),
    # path('sell/new/', SellCreateView.as_view(), name="create-sell"),
    # path('sell/new/<date:date>/', SellCreateView.as_view(), name="create-sell"),
    path('sell/new/multi/<date:date>/', MultiSellCreateView, name="create-sell-multi"),
    path('sell/<int:pk>/update/', SellUpdateView.as_view(), name="update-sell"),
    path('sell/<int:pk>/delete/', SellDeleteView.as_view(), name='delete-sell'),
    
]
