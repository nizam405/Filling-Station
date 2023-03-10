from django.urls import path, register_converter
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    WithdrawFormsetView, OwnersEquityDetailView,
    OwnersEquityView, InvestmentCreateView, InvestmentDeleteView, #, InvestmentUpdateView
    FixedAssetView, FixedAssetDeleteView,
)

urlpatterns = [
    # Withdraw
    path('withdraw/<date:date>/', WithdrawFormsetView, name="withdraw"),

    # Investment
    path('ownersequity/', OwnersEquityView.as_view(), name="ownersequity"),
    path('ownersequity/<int:pk>/<int:month>-<int:year>/details/', OwnersEquityDetailView.as_view(), name="ownersequity-details"),
    path('ownersequity/details/', OwnersEquityDetailView.as_view(), name="ownersequity-details"),
    path('investment/create/', InvestmentCreateView.as_view(), name="create-investment"),
    # path('investment/create/<date:date>/', InvestmentCreateView.as_view(), name="create-investment"),
    # path('investment/<int:pk>/update/', InvestmentUpdateView.as_view(), name="update-investment"),
    path('investment/<int:pk>/delete/', InvestmentDeleteView.as_view(), name="delete-investment"),

    # FixedAsset
    path('fixed-assets/', FixedAssetView.as_view(), name='fixed-assets'),
    path('fixed-assets/<int:pk>/delete/', FixedAssetDeleteView.as_view(), name='delete-fixedassets'),
]
