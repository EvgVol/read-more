from django.contrib import admin

from .models import Coupon


@admin.register(Coupon)
class CouponsAdmin(admin.ModelAdmin):
    list_display = ['code', 'valid_from', 'valid_to', 'discount', 'active']
    list_filter = ['active', 'valid_from', 'valid_to']
    search_fields = ['code']
