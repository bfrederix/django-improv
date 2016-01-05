from rest_framework import serializers

from channels.models import (Channel, ChannelAddress, SuggestionPool,
                             VoteType)


class ChannelAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChannelAddress
        fields = ('id', 'street', 'city', 'state',
                  'zipcode')


class ChannelSerializer(serializers.HyperlinkedModelSerializer):
    address = ChannelAddressSerializer(read_only=True)

    class Meta:
        model = Channel
        fields = ('id', 'name', 'display_name', 'is_premium',
                  'short_description', 'description',
                  'thumbnail_url', 'logo_url', 'team_photo_url',
                  'website', 'facebook_page', 'address',
                  'buy_tickets_link', 'next_show')


class SuggestionPoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuggestionPool
        fields = ('id', 'channel', 'name', 'display_name',
                  'description', 'max_user_suggestions', 'require_login',
                  'active', 'admin_only', 'created')


class VoteTypeSerializer(serializers.ModelSerializer):
    intervals = serializers.CharField(source='stripped_intervals')
    style = serializers.IntegerField(source='style_id')

    class Meta:
        model = VoteType
        fields = ('id', 'channel', 'name', 'display_name',
                  'suggestion_pool', 'preshow_voted',
                  'manual_interval_control', 'intervals', 'style',
                  'ordering', 'options', 'vote_length', 'result_length',
                  'button_color', 'require_login', 'active',
                  'current_interval', 'current_init', 'created')


class VoteStyleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        fields = ('id', 'name')