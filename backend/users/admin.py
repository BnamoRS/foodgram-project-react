from django.contrib import admin
from django.contrib.auth import get_user_model


User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'password', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')
    list_editable = (
        'username', 'password', 'email', 'first_name', 'last_name',
    )


admin.site.register(User, UserAdmin)
