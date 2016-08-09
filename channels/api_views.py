import logging

from rest_framework import viewsets
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from channels.models import (Channel, ChannelAddress, SuggestionPool,
                             VoteType, VOTE_STYLE)
from channels.serializers import (ChannelSerializer, ChannelAddressSerializer,
                                  SuggestionPoolSerializer, VoteTypeSerializer,
                                  VoteStyleSerializer)
from channels import service as channels_service
from shows import service as shows_service
from utilities.api import APIObject
from utilities import views as view_utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoteTypeAPIObject(APIObject):
    field_list = ['id', 'channel', 'name', 'display_name',
                  'manual_interval_control', 'stripped_intervals', 'style_id',
                  'ordering', 'options', 'vote_length', 'result_length',
                  'button_color', 'require_login', 'preshow_selected',
                  'player_options', 'players_only', 'show_player_pool',
                  'vote_type_player_pool', 'eliminate_winning_player',
                  'keep_suggestions', 'active', 'vote_options_name',
                  'current_interval', 'current_vote_init',
                  'interval_seconds_remaining', 'vote_seconds_remaining',
                  'remaining_intervals', 'created', 'no_randomize',
                  'hide_display_vote_count', 'hide_recap_vote_count',
                  'show_option_values']

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
            # Get the current voted item if it exists
            voted_item = shows_service.get_current_voted(show_id,
                                                         vote_type.id,
                                                         vote_type.current_interval)
            # If there was a winning voted item
            if voted_item:
                # Determine if an item has been voted for
                if vote_type.keep_suggestions:
                    self.vote_type_used = False
                else:
                    self.vote_type_used = True
                # Get the voted option for this vote type (interval)
                self.voted_option = voted_item.vote_option_id
                # Get the live votes for this vote type (interval)
                self.live_votes = shows_service.get_option_live_votes(voted_item.vote_option_id)
            # If intervals are automatic
            # and we have a current interval
            # and there are still intervals remaining
            # and the current interval has ended
            if not vote_type.manual_interval_control \
                and vote_type.current_interval != None \
                and vote_type.remaining_intervals() \
                and vote_type.interval_seconds_remaining() == 0:
                logger.info("Starting new interval")
                # Start the next interval for the show for the given vote type
                view_utils.start_new_interval(show, vote_type)


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
            queryset = SuggestionPool.objects.filter(**kwargs).exclude(archived=True)
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
        queryset = VoteType.objects.filter(**kwargs).exclude(archived=True)
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


class ChannelNameViewSet(viewsets.ViewSet):
    """
    API endpoint that gets a list of channel names by a query value
    """

    def list(self, request):
        exists = False
        query = self.request.query_params.get('q', '').lower()
        try:
            Channel.objects.get(name=query)
        except ObjectDoesNotExist:
            exists = False
        else:
            exists = True
        return Response(exists)