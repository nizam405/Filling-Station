from django.urls import path, register_converter
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    OwnerListView, 
    OwnerCreateView, OwnerUpdateView, OwnerDeleteView,
    WithdrawListView, WithdrawCreateView, WithdrawUpdateView, WithdrawDeleteView,
    InvestmentListView, InvestmentCreateView, InvestmentUpdateView, InvestmentDeleteView
)

urlpatterns = [
    # Owner
    path('list/', OwnerListView.as_view(), name="owner-list"),
    path('create/', OwnerCreateView.as_view(), name="create-owner"),
    path('<int:pk>/update/', OwnerUpdateView.as_view(), name="update-owner"),
    path('<int:pk>/delete/', OwnerDeleteView.as_view(), name="delete-owner"),

    # Withdraw
    # path('withdraw/list/', WithdrawListView.as_view(), name="withdraw-list"),
    path('withdraw/create/', WithdrawCreateView.as_view(), name="create-withdraw"),
    path('withdraw/create/<date:date>/', WithdrawCreateView.as_view(), name="create-withdraw"),
    path('withdraw/<int:pk>/update/', WithdrawUpdateView.as_view(), name="update-withdraw"),
    path('withdraw/<int:pk>/delete/', WithdrawDeleteView.as_view(), name="delete-withdraw"),

    # Investment
    path('investment/list/', InvestmentListView.as_view(), name="investment-list"),
    path('investment/create/', InvestmentCreateView.as_view(), name="create-investment"),
    path('investment/create/<date:date>/', InvestmentCreateView.as_view(), name="create-investment"),
    path('investment/<int:pk>/update/', InvestmentUpdateView.as_view(), name="update-investment"),
    path('investment/<int:pk>/delete/', InvestmentDeleteView.as_view(), name="delete-investment"),
]
