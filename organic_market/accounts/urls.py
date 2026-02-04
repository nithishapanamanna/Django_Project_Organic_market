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
from django.urls import path
from django.conf.urls.static import static
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_choice, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/farmers/', views.verify_farmers, name='verify_farmers'),
    path('admin/approve-farmer/<int:farmer_id>/', views.approve_farmer, name='approve_farmer'),
    path('admin/farmers/reject/<int:farmer_id>/', views.reject_farmer, name='reject_farmer'),
    path('products/', views.approve_products, name='approve_products'),
    path('admin/orders/', views.manage_orders, name='manage_orders'),
    path('users/', views.manage_users, name='manage_users'),
    path('payments/', views.manage_payments, name='manage_payments'),
    path('admin/users/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
