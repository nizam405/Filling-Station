from django.urls import path, register_converter, re_path
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    CashBalanceListView, CashBalanceCreateView,  CashBalanceUpdateView, CashBalanceDeleteView,
    DailyTransactionView)

urlpatterns = [
    path('', DailyTransactionView.as_view(), name='daily-transactions'),
    path('<date:date>/', DailyTransactionView.as_view(), name='daily-transactions'),

    # Cashbalance
    path('cashbalance-list/', CashBalanceListView.as_view(), name="cashbalance-list"),
    path('cashbalance/new/', CashBalanceCreateView.as_view(), name="create-cashbalance"),
    path('cashbalance/new/<date:date>/', CashBalanceCreateView.as_view(), name="create-cashbalance"),
    path('cashbalance/<int:pk>/update/', CashBalanceUpdateView.as_view(), name="update-cashbalance"),
    path('cashbalance/<int:pk>/delete/', CashBalanceDeleteView.as_view(), name="delete-cashbalance"),
]
