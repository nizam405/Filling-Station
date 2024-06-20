from django.urls import path, include
from .views import DocumentationHome

urlpatterns = [
    path('', DocumentationHome.as_view(), name='documentation-home'),
]
