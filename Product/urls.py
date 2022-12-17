from django.urls import path, register_converter
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView,
    SellingRateListView, SellingRateCreateView, SellingRateUpdateView, SellingRateDeleteView,
    SellListView, SellCreateView, SellUpdateView, SellDeleteView,
    PurchaseListView, PurchaseCreateView, PurchaseUpdateView, PurchaseDeleteView,
    
    )

urlpatterns = [
    # Product
    path('product-list/', ProductListView.as_view(), name='product-list'),
    path('product/new/', ProductCreateView.as_view(), name="create-product"),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name="update-product"),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='delete-product'),
    
    # Selling Rate
    path('selling-rates/', SellingRateListView.as_view(), name='selling-rates'),
    path('selling-rate/new/', SellingRateCreateView.as_view(), name="create-selling-rate"),
    path('selling-rate/<int:pk>/update/', SellingRateUpdateView.as_view(), name="update-selling-rate"),
    path('selling-rate/<int:pk>/delete/', SellingRateDeleteView.as_view(), name='delete-selling-rate'),
    
    # Purchase
    # path('purchases/', PurchaseListView.as_view(), name='purchases'),
    path('purchase/new/', PurchaseCreateView.as_view(), name="create-purchase"),
    path('purchase/new/<date:date>/', PurchaseCreateView.as_view(), name="create-purchase"),
    path('purchase/<int:pk>/update/', PurchaseUpdateView.as_view(), name="update-purchase"),
    path('purchase/<int:pk>/delete/', PurchaseDeleteView.as_view(), name='delete-purchase'),
    
    # Sells
    # path('sells/', SellListView.as_view(), name='sells'),
    path('sell/new/', SellCreateView.as_view(), name="create-sell"),
    path('sell/new/<date:date>/', SellCreateView.as_view(), name="create-sell"),
    path('sell/<int:pk>/update/', SellUpdateView.as_view(), name="update-sell"),
    path('sell/<int:pk>/delete/', SellDeleteView.as_view(), name='delete-sell'),
    
]
