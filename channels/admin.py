from django.contrib import admin
from channels.models import (Channel, ChannelAddress, ChannelUser,
                             ChannelAdminInvite, ChannelOwner,
                             SuggestionPool, VoteType)
from channels.models import ChannelAdmin as ModelChannelAdmin


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    pass


@admin.register(ChannelAddress)
class ChannelAddressAdmin(admin.ModelAdmin):
    pass


@admin.register(ChannelOwner)
class ChannelOwnerAdmin(admin.ModelAdmin):
    pass


@admin.register(ModelChannelAdmin)
class ChannelAdminAdmin(admin.ModelAdmin):
    pass


@admin.register(ChannelUser)
class ChannelUserAdmin(admin.ModelAdmin):
    pass


@admin.register(ChannelAdminInvite)
class ChannelAdminInviteAdmin(admin.ModelAdmin):
    pass


@admin.register(VoteType)
class VoteTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'display_name', 'suggestion_pool',
                    'intervals', 'style', 'ordering')


@admin.register(SuggestionPool)
class SuggestionPoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'channel', 'name', 'display_name')
