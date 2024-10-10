"""django_ideal_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# import debug_toolbar

from .views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('Account.urls')),
    path('settings/', include("Core.urls")),
    path('', HomeView.as_view(), name="home"), # Currently redirects to 'daily-transactions'
    path('transactions/', include("Transaction.urls")),
    path('ledgers/', include("Ledger.urls")),
    path('loan/', include("Loan.urls")),
    path('customer/', include("Customer.urls")),
    path('expenditure/', include("Expenditure.urls")),
    path('owner/', include("Owner.urls")),
    path('product/', include("Product.urls")),
    path('revenue/', include("Revenue.urls")),
    path('documentation/', include("Documentation.urls")),
]

if settings.DEBUG:
    # urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    
    # Serving static files during development (automatically does this)
    # If you don’t have django.contrib.staticfiles in INSTALLED_APPS
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Serving files uploaded by a user during development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
