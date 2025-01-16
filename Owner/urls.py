from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from . import views

urlpatterns = [
    # Withdraw
    path('withdraw/<date:date>/', include([
        path('create/', views.WithdrawCreateView.as_view(), name='create-withdraw'),
        path('<int:pk>/', include([
            path('update/', views.WithdrawUpdateView.as_view(), name='update-withdraw'),
            path('delete/', views.WithdrawDeleteView.as_view(), name='delete-withdraw'),
        ])),
        path('ledger/', views.WithdrawLedgerView.as_view(), name='withdraw-ledger'),
        path('ledger/<int:owner>/', views.WithdrawLedgerView.as_view(), name='withdraw-ledger'),
    ])),

    # Investment
    path('ownersequity/', include([
        path('', views.OwnersEquityView.as_view(), name="ownersequity"),
        path('<int:owner>/<date:date>/', views.OwnersEquityDetailView.as_view(), name="ownersequity-details"),
    ])),
    # path('investment/create/', views.InvestmentCreateView.as_view(), name="create-investment"),
    path('investment/create/<date:date>/', views.InvestmentCreateView.as_view(), name="create-investment"),
    path('investment/<date:date>/<int:pk>/update/', views.InvestmentUpdateView.as_view(), name="update-investment"),
    path('investment/<int:pk>/delete/', views.InvestmentDeleteView.as_view(), name="delete-investment"),

    # FixedAsset
    path('fixed-assets/', views.FixedAssetView.as_view(), name='fixed-assets'),
    path('fixed-assets/<int:pk>/delete/', views.FixedAssetDeleteView.as_view(), name='delete-fixedassets'),
]
