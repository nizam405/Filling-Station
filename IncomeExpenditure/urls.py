from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from . import views

urlpatterns = [
    path('income/', include([
        # Income Group
        path('group/', include([
            path('',  views.IncomeGroupCreateView.as_view(), name="create-income-group"),
            path('<int:pk>/', include([
                path('update/',  views.IncomeGroupUpdateView.as_view(), name="update-income-group"),
                path('delete/',  views.IncomeGroupDeleteView.as_view(), name="delete-income-group"),
            ]))
        ])),

        # Income
        path('<date:date>/', include([
            path('create/', views.IncomeCreateView.as_view(), name='create-income'),
            path('<int:pk>/', include([
                path('update/', views.IncomeUpdateView.as_view(), name='update-income'),
                path('delete/', views.IncomeDeleteView.as_view(), name='delete-income'),
            ])),
        ])),
    ])),

    path('expenditure/', include([
        # Expenditure Group
        path('group/', include([
            path('',  views.ExpenditureGroupCreateView.as_view(), name="create-expenditure-group"),
            path('<int:pk>/', include([
                path('update/',  views.ExpenditureGroupUpdateView.as_view(), name="update-expenditure-group"),
                path('delete/',  views.ExpenditureGroupDeleteView.as_view(), name="delete-expenditure-group"),
            ]))
        ])),

        # Expenditure
        path('<date:date>/', include([
            path('create/', views.ExpenditureCreateView.as_view(), name='create-expenditure'),
            path('<int:pk>/', include([
                path('update/', views.ExpenditureUpdateView.as_view(), name='update-expenditure'),
                path('delete/', views.ExpenditureDeleteView.as_view(), name='delete-expenditure'),
            ])),
        ])),
    ])),
    
    # Ledger
    path('ledger/', include([
        path('<date:date>/',include([
            path('income/', views.IncomeLedgerColumnView.as_view(), name='income-ledger-column'),
            path('expenditure/', views.ExpenditureLedgerColumnView.as_view(), name='expenditure-ledger-column'),
        ])),
    ])),
    # Income Statement
    path('incomestatement/', include([
        path('', views.IncomeStatementView.as_view(), name='incomestatement'),
        path('<date:date>/', views.IncomeStatementView.as_view(), name='incomestatement'),
    ])),
]