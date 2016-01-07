from rest_framework import viewsets
from rest_framework.response import Response

from leaderboards import LEADERBOARD_MAX_PER_PAGE
from leaderboards.models import LeaderboardEntry, Medal, LeaderboardSpan
from leaderboards.serializers import (LeaderboardEntrySerializer, MedalSerializer,
                                      LeaderboardSerializer, LeaderboardSpanSerializer)
from leaderboards import service as leaderboards_service
from users import service as users_service
from channels import service as channels_service
from utilities.api import APIObject


class LeaderboardEntryAPIObject(APIObject):
    field_list = ['id',
                  'user_id',
                  'points',
                  'wins']

    def __init__(self, leaderboard_entry, **kwargs):
        super(LeaderboardEntryAPIObject, self).__init__(leaderboard_entry, **kwargs)
        self.show = leaderboard_entry.show.id
        self.channel_name = leaderboard_entry.channel.name
        user_profile = users_service.fetch_user_profile(leaderboard_entry.user.id)
        self.username = user_profile.safe_username
        self.medals = [lem.medal.id for lem in leaderboards_service.fetch_medals_by_leaderboard_entry(leaderboard_entry)]



class LeaderboardAPIObject(APIObject):
    field_list = ['id',
                  'points',
                  'suggestion_wins',
                  'show_wins']

    def __init__(self, channel_user, **kwargs):
        super(LeaderboardAPIObject, self).__init__(channel_user, **kwargs)
        self.channel_name = channel_user.channel.name
        user_profile = users_service.fetch_user_profile(channel_user.user.id)
        self.user_id = channel_user.user.id
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
        order_by_show_date = self.request.query_params.get('order_by_show_date')
        if user_id:
            kwargs['user'] = user_id
        if channel_id:
            kwargs['channel'] = channel_id
        if show_id:
            kwargs['show'] = show_id
        queryset = LeaderboardEntry.objects.filter(**kwargs)
        if order_by_show_date is not None:
            queryset = queryset.order_by('-show_date')
        if show_id:
            queryset = queryset.order_by('-wins', '-points')
        leaderboard_entry_list = [LeaderboardEntryAPIObject(item) for item in queryset]
        serializer = LeaderboardEntrySerializer(leaderboard_entry_list, many=True)
        return Response(serializer.data)

class LeaderboardViewSet(viewsets.ViewSet):
    """
    API endpoint for show, channel, or combined leaderboards
    """

    def list(self, request):
        channel_id = self.request.query_params.get('channel_id')
        page = int(self.request.query_params.get('page', 1))
        offset = LEADERBOARD_MAX_PER_PAGE * (page - 1)
        channel = channels_service.channel_or_404(channel_id, channel_id=True)
        queryset = channels_service.fetch_channel_users(channel.id,
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