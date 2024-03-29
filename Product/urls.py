from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    ProductView, ProductUpdateView, change_product_status,
    RateCreateView, RateUpdateView, RateDeleteView,
    StorageReadingView, StorageReadingtUpdateView, StorageReadingDeleteView,
    SellFormsetView, PurchaseFormsetView
    )

urlpatterns = [
    path('', ProductView.as_view(), name='products'),
    path('<int:pk>/update/', ProductUpdateView.as_view(), name="update-product"),
    path('<int:pk>/status/', change_product_status, name="change-product-status"),
    path('purchase/<date:date>/', PurchaseFormsetView, name="purchase"),
    path('sell/<date:date>/', SellFormsetView, name="sell"),
    path('<int:product>/rate/', include([
        path('create/', RateCreateView.as_view(), name='rates'),
        path('<int:pk>/update/', RateUpdateView.as_view(), name='update-rate'),
        path('<int:pk>/delete/', RateDeleteView.as_view(), name='delete-rate'),
    ])),
    path('storage/', include([
        path('', StorageReadingView.as_view(), name='daily-product-storage'),
        path('<date:date>/', StorageReadingView.as_view(), name='daily-product-storage'),
        path('<int:pk>/update/', StorageReadingtUpdateView.as_view(), name='update-daily-product-storage'),
        path('<date:date>/<int:pk>/update/', StorageReadingtUpdateView.as_view(), name='update-daily-product-storage'),
        path('<int:pk>/delete/', StorageReadingDeleteView.as_view(), name='delete-daily-product-storage'),
    ])),
]
