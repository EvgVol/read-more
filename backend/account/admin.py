from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'first_name', 'last_name',
                    'birthdate', 'phone_number', 'is_staff']
    list_editable = ('is_staff',)
    list_filter = ('username', )
    search_fields = ('username', )
    # search_fields = ['title', 'body']
    # prepopulated_fields = {'slug': ('title',)}
    # raw_id_fields = ['author']
    # date_hierarchy = 'publish'
    # ordering = ['-publish', 'status']
