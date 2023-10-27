from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    CashBalanceListView, CashBalanceCreateView,  CashBalanceUpdateView, CashBalanceDeleteView,
    DailyTransactionView, CashBalanceControlView)

urlpatterns = [
    path('', DailyTransactionView.as_view(), name='daily-transactions'),
    path('<date:date>/', DailyTransactionView.as_view(), name='daily-transactions'),

    # Cashbalance
    path('cashbalance/', include([
        path('list/', CashBalanceListView.as_view(), name="cashbalance-list"),
        path('control/', CashBalanceControlView.as_view(), name="cashbalance-control"),
        path('new/', CashBalanceCreateView.as_view(), name="create-cashbalance"),
        path('new/<date:date>/', CashBalanceCreateView.as_view(), name="create-cashbalance"),
        # path('<int:pk>/update/', CashBalanceUpdateView.as_view(), name="update-cashbalance"),
        path('<int:pk>/delete/', CashBalanceDeleteView.as_view(), name="delete-cashbalance"),
    ])),
]
