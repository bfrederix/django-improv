import datetime
from rest_framework import viewsets
from rest_framework.response import Response

from leaderboards import LEADERBOARD_MAX_PER_PAGE
from leaderboards.models import LeaderboardEntry, Medal, LeaderboardSpan
from leaderboards.serializers import (LeaderboardEntrySerializer, MedalSerializer,
                                      LeaderboardSerializer, LeaderboardSpanSerializer,
                                      LeaderboardEntrySpanSerializer)
from leaderboards import service as leaderboards_service
from users import service as users_service
from channels import service as channels_service
from shows import service as shows_service
from utilities.api import APIObject


class LeaderboardEntryAPIObject(APIObject):
    field_list = ['id',
                  'user_id',
                  'points',
                  'wins']

    def __init__(self, leaderboard_entry, **kwargs):
        super(LeaderboardEntryAPIObject, self).__init__(leaderboard_entry, **kwargs)
        self.show = leaderboard_entry.show_id
        self.channel_name = leaderboard_entry.channel.name
        self.medals = leaderboards_service.fetch_medal_ids_by_leaderboard_entry(leaderboard_entry.id)
        # If a user is attached to the entry
        if leaderboard_entry.user_id:
            # Get their username
            user_profile = users_service.fetch_user_profile(leaderboard_entry.user_id)
            self.username = user_profile.safe_username
            # Get the number of suggestions submitted
            self.suggestions = shows_service.fetch_suggestions(user_id=leaderboard_entry.user_id,
                                                               show_id=leaderboard_entry.show_id,
                                                               count=True)


class LeaderboardEntrySpanAPIObject(APIObject):

    def __init__(self, leaderboard_span_entry, **kwargs):
        super(LeaderboardEntrySpanAPIObject, self).__init__(leaderboard_span_entry, **kwargs)
        self.channel_name = kwargs.get('channel_name')
        self.user_id = leaderboard_span_entry['user_id']
        user_profile = users_service.fetch_user_profile(self.user_id)
        self.username = user_profile.safe_username
        self.points = leaderboard_span_entry['points']
        self.show_wins = leaderboard_span_entry['show_wins']
        self.suggestion_wins = leaderboard_span_entry['suggestion_wins']


class LeaderboardAPIObject(APIObject):
    field_list = ['id',
                  'points',
                  'suggestion_wins',
                  'show_wins']

    def __init__(self, channel_user, **kwargs):
        super(LeaderboardAPIObject, self).__init__(channel_user, **kwargs)
        self.channel_name = kwargs.get('channel_name')
        user_profile = users_service.fetch_user_profile(channel_user.user_id)
        self.user_id = channel_user.user_id
        self.username = user_profile.safe_username


class LeaderboardEntryViewSet(viewsets.ViewSet):
    """
    API endpoint that returns leaderboard entries
    """

    def list(self, request):
        kwargs = {}
        user_id = self.request.query_params.get('user_id')
        channel_id = self.request.query_params.get('channel_id')
        show_id = self.request.query_params.get('show_id')
        limit = self.request.query_params.get('limit')
        # Pagination
        page = int(self.request.query_params.get('page', 1))
        offset = LEADERBOARD_MAX_PER_PAGE * (page - 1)
        order_by_show_date = self.request.query_params.get('order_by_show_date')
        if user_id:
            kwargs['user'] = user_id
        if channel_id:
            kwargs['channel'] = channel_id
        if show_id:
            kwargs['show'] = show_id
        # Make sure we exclude any entries that don't have users attached
        queryset = LeaderboardEntry.objects.filter(**kwargs).exclude(user=None)
        # If we are ordering by when the show happened
        if order_by_show_date is not None:
            queryset = queryset.order_by('-show_date')
        # Order by suggestion wins, then points for a show or span
        if show_id:
            queryset = queryset.order_by('-wins', '-points')
        # If there is a limit to the results returned
        if limit:
            queryset = queryset[:int(limit)]
        # Start from the page offset
        try:
            queryset = queryset[offset:offset+LEADERBOARD_MAX_PER_PAGE]
        except IndexError:
            try:
                queryset = queryset[offset:]
            except IndexError:
                pass
        leaderboard_entry_list = [LeaderboardEntryAPIObject(item) for item in queryset]
        serializer = LeaderboardEntrySerializer(leaderboard_entry_list, many=True)
        return Response(serializer.data)


class LeaderboardEntrySpanViewSet(viewsets.ViewSet):
    """
    API endpoint that returns leaderboard entries by span dates
    """

    def list(self, request):
        kwargs = {}
        kwargs['channel'] = self.request.query_params.get('channel_id')
        channel = channels_service.channel_or_404(kwargs['channel'], channel_id=True)
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        # Convert start and end to datetimes
        start_time = datetime.datetime.strptime(start, "%Y%m%d")
        end_time = datetime.datetime.strptime(end, "%Y%m%d")
        # Add them to the queryset params
        kwargs['show_date__gte'] = start_time
        kwargs['show_date__lte'] = end_time
        # Make sure we exclude any entries that don't have users attached
        queryset = LeaderboardEntry.objects.filter(**kwargs).exclude(user=None)
        # Aggregate all the leaderboard entries by the user
        leaderboard_aggregate = leaderboards_service.aggregate_leaderboard_entries_by_user(
                                    queryset)
        api_kwargs = {'channel_name': channel.name}
        # Make an api object out of the user aggregates
        leaderboard_entry_list = [LeaderboardEntrySpanAPIObject(item, **api_kwargs) for item in leaderboard_aggregate]
        serializer = LeaderboardEntrySpanSerializer(leaderboard_entry_list, many=True)
        return Response(serializer.data)


class LeaderboardViewSet(viewsets.ViewSet):
    """
    API endpoint for show, channel, or combined leaderboards
    """

    def list(self, request):
        channel_id = self.request.query_params.get('channel_id')
        page = int(self.request.query_params.get('page', 1))
        offset = LEADERBOARD_MAX_PER_PAGE * (page - 1)
        queryset = channels_service.fetch_channel_users(channel_id,
                                                        leaderboard_sort=True)
        # Start from the page offset
        try:
            queryset = queryset[offset:offset+LEADERBOARD_MAX_PER_PAGE]
        except IndexError:
            try:
                queryset = queryset[offset:]
            except IndexError:
                pass
        leaderboard_list = [LeaderboardAPIObject(item) for item in queryset]
        serializer = LeaderboardSerializer(leaderboard_list, many=True)
        return Response(serializer.data)


class LeaderboardSpanViewSet(viewsets.ViewSet):
    """
    API endpoint that allows leaderboard spans to be viewed
    """

    def retrieve(self, request, pk=None):
        leaderboard_span = leaderboards_service.leaderboard_span_or_404(pk)
        serializer = LeaderboardSpanSerializer(leaderboard_span)
        return Response(serializer.data)

    def list(self, request):
        """
        This view should return a list of all leaderboard spans
        """
        queryset = LeaderboardSpan.objects.all()
        channel_id = self.request.query_params.get('channel_id')
        if channel_id:
            queryset = queryset.filter(channel=channel_id)
        serializer = LeaderboardSpanSerializer(queryset, many=True)
        return Response(serializer.data)


class MedalViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows medals to be viewed
    """
    model = Medal
    serializer_class = MedalSerializer
    queryset = Medal.objects.all()