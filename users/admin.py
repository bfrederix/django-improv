from django.contrib import admin
from users.models import (UserProfile, UserChannelEmailOptIn)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'username', 'email', 'login_type', 'created')
    list_display_links = ('user',)


@admin.register(UserChannelEmailOptIn)
class UserChannelEmailOptInAdmin(admin.ModelAdmin):
    pass
