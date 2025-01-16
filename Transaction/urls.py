from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from . import views

urlpatterns = [
    path('', views.DailyTransactionView.as_view(), name='daily-transactions'),
    path('<date:date>/', views.DailyTransactionView.as_view(), name='daily-transactions'),
    path('save-cashbalance/<date:date>:<str:amount>/', views.SaveDailyCashBalanceView.as_view(), name='save-daily-cashbalance'),

    # Cashbalance
    path('cashbalance/', include([
        path('list/', views.CashBalanceListView.as_view(), name="cashbalance-list"),
        path('control/', views.CashBalanceControlView.as_view(), name="cashbalance-control"),
        path('new/<date:date>/', views.CashBalanceCreateView.as_view(), name="create-cashbalance"),
        path('<int:pk>/update/', views.CashBalanceUpdateView.as_view(), name="update-cashbalance"),
        path('<int:pk>/delete/', views.CashBalanceDeleteView.as_view(), name="delete-cashbalance"),
    ])),
]
