from django.urls import path
from Account.views import (
    UserLoginView, UserLogoutView, 
    UserPasswordChangeView, UserPasswordChangeDoneView,
    )

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('change-password/', UserPasswordChangeView.as_view(), name='password-change'),
    path('change-password/done/', UserPasswordChangeDoneView.as_view(), name='password-change-done'),
]
