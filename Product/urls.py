from django.urls import path, register_converter
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    ProductView, ProductUpdateView, ProductDeleteView, 
    SellFormsetView, PurchaseFormsetView,
    )

urlpatterns = [
    path('', ProductView.as_view(), name='products'),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name="update-product"),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='delete-product'),
    path('product/purchase/<date:date>/', PurchaseFormsetView, name="purchase"),
    path('product/sell/<date:date>/', SellFormsetView, name="sell"),
]
