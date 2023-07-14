from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['author', 'content_type', 'object_id', 'rating', 'comment']
