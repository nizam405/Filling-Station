from django.urls import path, register_converter
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import LedgerList

urlpatterns = [
    path('', LedgerList.as_view(), name='ledger-list'),
]
