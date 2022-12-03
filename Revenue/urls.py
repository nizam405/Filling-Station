from django.urls import path
from .views import (
    RevenueGroupListView, RevenueGroupCreateView, RevenueGroupUpdateView, RevenueGroupDeleteView,
    RevenueListView, RevenueCreateView, RevenueUpdateView, RevenueDeleteView,
)

urlpatterns = [
    # Revenue Group
    path('group/list/',  RevenueGroupListView.as_view(), name="revenuegroup-list"),
    path('group/create/',  RevenueGroupCreateView.as_view(), name="create-revenuegroup"),
    path('group/<int:pk>/update/',  RevenueGroupUpdateView.as_view(), name="update-revenuegroup"),
    path('group/<int:pk>/delete/',  RevenueGroupDeleteView.as_view(), name="delete-revenuegroup"),

    # Revenue
    path('list/',  RevenueListView.as_view(), name="revenue-list"),
    path('create/',  RevenueCreateView.as_view(), name="create-revenue"),
    path('<int:pk>/update/',  RevenueUpdateView.as_view(), name="update-revenue"),
    path('<int:pk>/delete/',  RevenueDeleteView.as_view(), name="delete-revenue"),
]
