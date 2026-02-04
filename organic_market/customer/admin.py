from django.contrib import admin
from .models import CustomerProfile

@admin.register(CustomerProfile)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_verified')
    list_filter = ('is_verified',)
    actions = ['verify_customers']

    def verify_customers(self, request, queryset):
        queryset.update(is_verified=True)
