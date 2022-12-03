from django.urls import path
from .views import (
    ExpenditureGroupListView, ExpenditureGroupCreateView, ExpenditureGroupUpdateView, ExpenditureGroupDeleteView,
    ExpenditureListView, ExpenditureCreateView, ExpenditureUpdateView, ExpenditureDeleteView,
)

urlpatterns = [
    # Expenditure Group
    path('group/list/',  ExpenditureGroupListView.as_view(), name="expendituregroup-list"),
    path('group/create/',  ExpenditureGroupCreateView.as_view(), name="create-expendituregroup"),
    path('group/<int:pk>/update/',  ExpenditureGroupUpdateView.as_view(), name="update-expendituregroup"),
    path('group/<int:pk>/delete/',  ExpenditureGroupDeleteView.as_view(), name="delete-expendituregroup"),

    # Expenditure
    path('list/',  ExpenditureListView.as_view(), name="expenditure-list"),
    path('create/',  ExpenditureCreateView.as_view(), name="create-expenditure"),
    path('<int:pk>/update/',  ExpenditureUpdateView.as_view(), name="update-expenditure"),
    path('<int:pk>/delete/',  ExpenditureDeleteView.as_view(), name="delete-expenditure"),
]
