from django.contrib import admin
from users.models import (UserProfile, EmailOptOut)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'username', 'is_admin', 'email', 'login_type', 'created')
    list_display_links = ('id',)


@admin.register(EmailOptOut)
class EmailOptOutAdmin(admin.ModelAdmin):
    pass
