from django.urls import path
from .views import (
    OwnerListView, OwnerDetailView,
    OwnerCreateView, OwnerUpdateView, OwnerDeleteView,
)

urlpatterns = [
    path('list/', OwnerListView.as_view(), name="owner-list"),
    path('<int:pk>/detail/', OwnerDetailView.as_view(), name="owner-detail"),
    path('create/', OwnerCreateView.as_view(), name="create-owner"),
    path('<int:pk>/update/', OwnerUpdateView.as_view(), name="update-owner"),
    path('<int:pk>/delete/', OwnerDeleteView.as_view(), name="delete-owner"),
]
