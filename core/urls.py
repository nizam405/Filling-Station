from django.urls import path, include
from . import views

urlpatterns = [
    path('new/', views.SettingsCreateView.as_view(), name='create-settings'),
    path('<int:pk>/update/', views.SettingsUpdateView.as_view(), name='update-settings'),
]
