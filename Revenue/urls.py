from django.urls import path, register_converter
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    RevenueGroupView, RevenueGroupUpdateView, RevenueGroupDeleteView,
    RevenueUpdateView, RevenueDeleteView, MultiRevenueCreateView,
)

urlpatterns = [
    # Revenue Group
    path('group/',  RevenueGroupView.as_view(), name="revenue-group"),
    path('group/<int:pk>/update/',  RevenueGroupUpdateView.as_view(), name="update-revenuegroup"),
    path('group/<int:pk>/delete/',  RevenueGroupDeleteView.as_view(), name="delete-revenuegroup"),

    # Revenue
    # path('list/',  RevenueListView.as_view(), name="revenue-list"),
    # path('create/<date:date>',  RevenueCreateView.as_view(), name="create-revenue"),
    path('create/multi/<date:date>',  MultiRevenueCreateView, name="create-revenue-multi"),
    path('<int:pk>/update/',  RevenueUpdateView.as_view(), name="update-revenue"),
    path('<int:pk>/delete/',  RevenueDeleteView.as_view(), name="delete-revenue"),
]
