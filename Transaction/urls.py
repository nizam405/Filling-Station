from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from . import views

urlpatterns = [
    path('', views.DailyTransactionView.as_view(), name='daily-transactions'),
    path('<date:date>/', views.DailyTransactionView.as_view(), name='daily-transactions'),

    # Cashbalance
    path('cashbalance/', include([
        # path('list/', views.CashBalanceListView.as_view(), name="cashbalance-list"),
        path('control/', views.CashBalanceControlView.as_view(), name="cashbalance-control"),
        path('new/', views.CashBalanceCreateView.as_view(), name="create-cashbalance"),
        path('new/<date:date>/', views.CashBalanceCreateView.as_view(), name="create-cashbalance"),
        # path('<int:pk>/update/', CashBalanceUpdateView.as_view(), name="update-cashbalance"),
        path('<int:pk>/delete/', views.CashBalanceDeleteView.as_view(), name="delete-cashbalance"),
    ])),
    path('dailybalance/', include([
        path('list/', views.DailyBalanceListView.as_view(), name='dailybalance-list'),
        path('new/', views.DailyBalanceCreateView.as_view(), name='create-dailybalance'),
        path('new/<date:date>/', views.DailyBalanceCreateView.as_view(), name='create-dailybalance'),
        path('<int:pk>/update/', views.DailyBalanceUpdateView.as_view(), name='update-dailybalance'),
        path('<int:pk>/delete/', views.DailyBalanceDeleteView.as_view(), name='delete-dailybalance'),
    ])),
]
