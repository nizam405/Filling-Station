from django.urls import path, register_converter
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    ExpenditureGroupView, ExpenditureGroupUpdateView, ExpenditureGroupDeleteView,
    ExpenditureFormsetView
)

urlpatterns = [
    # Expenditure Group
    path('group/',  ExpenditureGroupView.as_view(), name="expenditure-group"),
    path('group/<int:pk>/update/',  ExpenditureGroupUpdateView.as_view(), name="update-expendituregroup"),
    path('group/<int:pk>/delete/',  ExpenditureGroupDeleteView.as_view(), name="delete-expendituregroup"),

    # Expenditure
    path('<date:date>/',  ExpenditureFormsetView, name="expenditure"),
]
