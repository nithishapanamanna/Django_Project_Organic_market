"""
URL configuration for organic_market project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import *

urlpatterns = [
    path('customer/register/', customer_register, name='customer_register'),
    path('customer/login/', customer_login, name='customer_login'),
    path('customer/dashboard/', customer_dashboard, name='customer_dashboard'),
    path('orders/', my_orders, name='my_orders'),
    path('customer/profile/', customer_profile, name='customer_profile'),
    path('customer/delete-account/', customer_delete_account, name='customer_delete_account')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
