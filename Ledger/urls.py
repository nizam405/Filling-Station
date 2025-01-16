from django.urls import path, register_converter, include
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import main
# from .views import customer_views
from .views import incomestatement_view

urlpatterns = [
    # path('withdraw/', include([
    #     path('', main.WithdrawLedger.as_view(), name='withdraw-ledger'),
    #     path('<int:month>-<int:year>/', main.WithdrawLedger.as_view(), name='withdraw-ledger'),
    # ])),
    # path('profit-adjustment/<int:month>-<int:year>/', incomestatement_view.ProfitAdjustment.as_view(), name='profit-adjustment'),
    
]
