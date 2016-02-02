from rest_framework import viewsets
from rest_framework.response import Response

from channels.models import (Channel, ChannelAddress, SuggestionPool,
                             VoteType, VOTE_STYLE)
from channels.serializers import (ChannelSerializer, ChannelAddressSerializer,
                                  SuggestionPoolSerializer, VoteTypeSerializer,
                                  VoteStyleSerializer)
from channels import service as channels_service
from shows import service as shows_service
from utilities.api import APIObject


class VoteTypeAPIObject(APIObject):
    field_list = ['id', 'channel', 'name', 'display_name',
                  'manual_interval_control', 'stripped_intervals', 'style_id',
                  'ordering', 'options', 'vote_length', 'result_length',
                  'button_color', 'require_login', 'preshow_selected',
                  'player_options', 'players_only', 'show_player_pool',
                  'vote_type_player_pool', 'eliminate_winning_player',
                  'keep_suggestions', 'active', 'vote_options_name',
                  'current_interval', 'current_vote_init',
                  'remaining_intervals', 'created']

    def __init__(self, vote_type, **kwargs):
        super(VoteTypeAPIObject, self).__init__(vote_type, **kwargs)
        self.suggestion_pool_id = vote_type.suggestion_pool_id
        show_id = kwargs.get('show_id')
        # If requesting data about a specific show's vote type
        if show_id:
            show = shows_service.show_or_404(show_id)
            # If it's player options
            if vote_type.players_only:
                # If it uses a pool for the show
                if vote_type.show_player_pool:
                    self.available_options = len(show.remaining_show_players())
                # If it's a pool for a specific vote type
                elif vote_type.vote_type_player_pool:
                    self.available_options = \
                            shows_service.get_show_vote_type_player_pool_ids(vote_type,
                                                                             show_id,
                                                                             count=True,
                                                                             used=False)
                # If it's all players for the show
                else:
                    self.available_options = len(show.players())
            # If it's a suggestion pool option
            elif self.suggestion_pool_id:
                self.available_options = shows_service.fetch_suggestions(show_id=show_id,
                                                                         suggestion_pool_id=self.suggestion_pool_id,
                                                                         count=True,
                                                                         used=False)
            else:
                raise ValueError("Something went wrong with this Vote Type: {0}".format(
                                    vote_type.id))
            # Determine if an item has been voted for
            self.vote_type_used = vote_type.vote_type_used(show)




class ChannelViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Channels
    """
    model = Channel
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()


class ChannelAddressViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Channel Addresses
    """
    model = ChannelAddress
    serializer_class = ChannelAddressSerializer
    queryset = ChannelAddress.objects.all()


class SuggestionPoolViewSet(viewsets.ViewSet):
    """
    API endpoint that allows suggestion pools to be viewed
    """

    def retrieve(self, request, pk=None):
        suggestion_pool = channels_service.suggestion_pool_or_404(pk)
        serializer = SuggestionPoolSerializer(suggestion_pool)
        return Response(serializer.data)

    def list(self, request):
        kwargs = {}
        channel_id = self.request.query_params.get('channel_id')
        show_id = self.request.query_params.get('show_id')
        sort_by_active = self.request.query_params.get('sort_by_active')
        active_only = self.request.query_params.get('active_only')
        # If pulling suggestion pools that are attached to a show
        if show_id:
            show = shows_service.show_or_404(show_id)
            # Get the vote types by a list of ids
            vote_types = channels_service.fetch_vote_types_by_ids(show.vote_types())
            # Get the suggestion pools from the vote types
            queryset = shows_service.get_vote_types_suggestion_pools(vote_types)
        # Any other suggestion pool fetching
        else:
            if channel_id:
                kwargs['channel'] = channel_id
            queryset = SuggestionPool.objects.filter(**kwargs)
            # Exclude non-active suggestion pools
            if active_only:
                queryset = queryset.exclude(active=False)
            if sort_by_active:
                queryset = queryset.order_by('-active', 'name')
        serializer = SuggestionPoolSerializer(queryset, many=True)
        return Response(serializer.data)


class VoteTypeViewSet(viewsets.ViewSet):
    """
    API endpoint that allows vote types to be viewed
    """

    def retrieve(self, request, pk=None):
        show_id = self.request.query_params.get('show_id')
        vote_type_kwargs = {'show_id': show_id}
        vote_type = channels_service.vote_type_or_404(pk)
        vote_type_api_obj = VoteTypeAPIObject(vote_type, **vote_type_kwargs)
        serializer = VoteTypeSerializer(vote_type_api_obj)
        return Response(serializer.data)

    def list(self, request):
        kwargs = {}
        channel_id = self.request.query_params.get('channel_id')
        sort_by_active = self.request.query_params.get('sort_by_active')
        active_only = self.request.query_params.get('active_only')
        if channel_id:
            kwargs['channel'] = channel_id
        queryset = VoteType.objects.filter(**kwargs)
        # Exclude non-active suggestion pools
        if active_only:
            queryset = queryset.exclude(active=False)
        if sort_by_active:
            queryset = queryset.order_by('-active', 'name')
        updated_vote_types = [VoteTypeAPIObject(item) for item in queryset]
        serializer = VoteTypeSerializer(updated_vote_types, many=True)
        return Response(serializer.data)


class VoteStyleViewSet(viewsets.ViewSet):
    """
    API endpoint that allows vote styles to be viewed
    """

    def retrieve(self, request, pk=None):
        style_id = int(pk)
        vote_style = channels_service.vote_style_or_404(style_id)
        style_dict = {'id': style_id, 'name': vote_style[1]}
        serializer = VoteStyleSerializer(style_dict)
        return Response(serializer.data)

    def list(self, request):
        vote_styles = []
        count = 0
        for (name, display_name) in VOTE_STYLE:
            count +=1
            vote_styles.append({'id': count, 'name': display_name})
        serializer = VoteStyleSerializer(vote_styles, many=True)
        return Response(serializer.data)