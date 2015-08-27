from django.contrib import admin
from channels.models import (Channel, ChannelAddress, ChannelUser,
                             ChannelAdminInvite, ChannelOwner)
from channels.models import ChannelAdmin as ModelChannelAdmin


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    pass


@admin.register(ChannelAddress)
class ChannelAddressAdmin(admin.ModelAdmin):
    pass


@admin.register(ChannelAdminInvite)
class ChannelAdminInviteAdmin(admin.ModelAdmin):
    pass
