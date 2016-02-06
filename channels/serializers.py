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
                  'thumbnail_url', 'team_photo_url',
                  'website', 'facebook_page', 'address',
                  'buy_tickets_link', 'next_show',
                  'navbar_color', 'background_color')


class SuggestionPoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuggestionPool
        fields = ('id', 'channel', 'name', 'display_name',
                  'description', 'max_user_suggestions', 'require_login',
                  'active', 'admin_only', 'created')


class VoteTypeSerializer(serializers.ModelSerializer):
    intervals = serializers.CharField(source='stripped_intervals')
    style = serializers.IntegerField(source='style_id')
    vote_options_name = serializers.CharField()
    suggestion_pool = serializers.IntegerField(required=False, source='suggestion_pool_id')
    available_options = serializers.IntegerField(required=False)
    vote_type_used = serializers.BooleanField(required=False)
    current_voted_suggestion = serializers.IntegerField(required=False)
    current_voted_player = serializers.IntegerField(required=False)
    live_votes = serializers.IntegerField(required=False)

    class Meta:
        model = VoteType
        fields = ('id', 'channel', 'name', 'display_name',
                  'suggestion_pool', 'available_options',
                  'manual_interval_control', 'intervals', 'style',
                  'ordering', 'options', 'vote_length', 'result_length',
                  'button_color', 'require_login', 'preshow_selected',
                  'player_options', 'players_only', 'show_player_pool',
                  'vote_type_player_pool', 'eliminate_winning_player',
                  'keep_suggestions', 'active', 'vote_options_name',
                  'current_interval', 'current_vote_init',
                  'interval_seconds_remaining', 'vote_seconds_remaining',
                  'remaining_intervals', 'vote_type_used', 'created',
                  'current_voted_suggestion', 'current_voted_player',
                  'live_votes')


class VoteStyleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()

    class Meta:
        fields = ('id', 'name')