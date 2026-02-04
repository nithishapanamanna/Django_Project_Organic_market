from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('farmer/dashboard/', farmer_dashboard, name='farmer_dashboard'),
    path('farmer/login/', farmer_login, name='farmer_login'),
    path('farmer/register/', farmer_register, name='farmer_register'),
    path('farmer/profile/', farmer_profile, name='farmer_profile'),
    path('add-product/', add_product, name='add_product'),
    path('farmer/product/<int:product_id>/edit/', edit_product, name='edit_product'),
    path('farmer/product/<int:product_id>/delete/', delete_product, name='delete_product'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
