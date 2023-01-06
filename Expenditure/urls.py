from django.urls import path, register_converter
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    ExpenditureGroupView, ExpenditureGroupUpdateView, ExpenditureGroupDeleteView,
    ExpenditureUpdateView, ExpenditureDeleteView, MultiExpenditureCreateView,
)

urlpatterns = [
    # Expenditure Group
    path('group/',  ExpenditureGroupView.as_view(), name="expenditure-group"),
    # path('group/create/',  ExpenditureGroupCreateView.as_view(), name="create-expendituregroup"),
    path('group/<int:pk>/update/',  ExpenditureGroupUpdateView.as_view(), name="update-expendituregroup"),
    path('group/<int:pk>/delete/',  ExpenditureGroupDeleteView.as_view(), name="delete-expendituregroup"),

    # Expenditure
    # path('list/',  ExpenditureListView.as_view(), name="expenditure-list"),
    # path('create/',  ExpenditureCreateView.as_view(), name="create-expenditure"),
    # path('create/<date:date>/',  ExpenditureCreateView.as_view(), name="create-expenditure"),
    path('multi-create/<date:date>/',  MultiExpenditureCreateView, name="create-expenditure-multi"),
    path('<int:pk>/update/',  ExpenditureUpdateView.as_view(), name="update-expenditure"),
    path('<int:pk>/delete/',  ExpenditureDeleteView.as_view(), name="delete-expenditure"),
]
