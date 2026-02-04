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

app_name = 'orders'

urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('place/', place_order, name='place_order'),
    path('my/', my_orders, name='my_orders'),
    path('razorpay/create/', create_razorpay_order, name='razorpay_create'),
    path('cancel/<int:order_id>/', cancel_order, name='cancel_order'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
