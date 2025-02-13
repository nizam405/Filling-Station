from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView

class UserLoginView(LoginView):
    template_name = 'Account/login.html'

class UserLogoutView(LogoutView):
    template_name = 'Account/logout.html'

class UserPasswordChangeView(PasswordChangeView):
    template_name = 'Account/change_password.html'
    success_url = reverse_lazy('password-change-done')

class UserPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'Account/password_change_done.html'

