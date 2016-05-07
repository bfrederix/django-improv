from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from channels.models import (Channel, ChannelAddress, ChannelUser,
                             ChannelOwner, SuggestionPool, VoteType)
from channels.models import ChannelAdmin as ModelChannelAdmin


class ChannelResource(resources.ModelResource):

    class Meta:
        model = Channel
        fields = ('id', 'email', 'name', 'display_name', 'premium', 'archived',)
        exclude = ('short_description', 'description', 'thumbnail_url',
                   'team_photo_url', 'website', 'facebook_page',
                   'facebook_pixel', 'buy_tickets_link', 'next_show',
                   'navbar_color', 'background_color', 'address', 'created',)
        export_order = ('id', 'email', 'name', 'display_name', 'premium', 'archived',)


@admin.register(Channel)
class ChannelAdmin(ImportExportModelAdmin):
    resource_class = ChannelResource


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


@admin.register(VoteType)
class VoteTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'display_name', 'suggestion_pool',
                    'intervals', 'style', 'ordering')


@admin.register(SuggestionPool)
class SuggestionPoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'channel', 'name', 'display_name')
