from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'password', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    list_editable = (
        'username', 'password', 'email', 'first_name', 'last_name',
    )
