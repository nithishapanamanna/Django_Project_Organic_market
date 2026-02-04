from django.contrib import admin
from .models import *

@admin.register(FarmerProfile)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'is_verified')
    list_filter = ('is_verified',)
    actions = ['verify_farmers']

    def verify_farmers(self, request, queryset):
        queryset.update(is_verified=True)
