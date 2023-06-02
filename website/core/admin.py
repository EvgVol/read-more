from django.contrib import admin

from .models import Policy


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ['id', 'publish', 'status']
    list_filter = ['status', 'created', 'publish']
    ordering = ['-publish', 'status']
