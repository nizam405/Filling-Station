from django.urls import path, register_converter
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    OwnerView, OwnerUpdateView, OwnerDeleteView,
    WithdrawFormsetView,
    # InvestmentListView, InvestmentCreateView, InvestmentUpdateView, InvestmentDeleteView
)

urlpatterns = [
    # Owner
    # path('list/', OwnerListView.as_view(), name="owner-list"),
    path('', OwnerView.as_view(), name="owners"),
    path('<int:pk>/update/', OwnerUpdateView.as_view(), name="update-owner"),
    path('<int:pk>/delete/', OwnerDeleteView.as_view(), name="delete-owner"),

    # Withdraw
    path('withdraw/<date:date>/', WithdrawFormsetView, name="withdraw"),

    # Investment
    # path('investment/list/', InvestmentListView.as_view(), name="investment-list"),
    # path('investment/create/', InvestmentCreateView.as_view(), name="create-investment"),
    # path('investment/create/<date:date>/', InvestmentCreateView.as_view(), name="create-investment"),
    # path('investment/<int:pk>/update/', InvestmentUpdateView.as_view(), name="update-investment"),
    # path('investment/<int:pk>/delete/', InvestmentDeleteView.as_view(), name="delete-investment"),
]
