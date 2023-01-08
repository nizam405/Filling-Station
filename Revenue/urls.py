from django.urls import path, register_converter
from Core.converters import DateConverter
register_converter(DateConverter, 'date')

from .views import (
    RevenueGroupView, RevenueGroupUpdateView, RevenueGroupDeleteView,
    RevenueFormsetView,
)

urlpatterns = [
    # Revenue Group
    path('group/',  RevenueGroupView.as_view(), name="revenue-group"),
    path('group/<int:pk>/update/',  RevenueGroupUpdateView.as_view(), name="update-revenuegroup"),
    path('group/<int:pk>/delete/',  RevenueGroupDeleteView.as_view(), name="delete-revenuegroup"),

    # Revenue
    path('<date:date>/',  RevenueFormsetView, name="revenue"),
]
