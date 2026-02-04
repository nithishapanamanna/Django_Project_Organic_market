from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'price', 'is_approved')
    list_filter = ('is_approved',)
    actions = ['approve_products']

    def approve_products(self, request, queryset):
        queryset.update(is_approved=True)
