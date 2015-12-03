from rest_framework import viewsets
from rest_framework.response import Response

from leaderboards.models import LeaderboardEntry, Medal, LeaderboardSpan
from leaderboards.serializers import (LeaderboardEntrySerializer, MedalSerializer,
                                      LeaderboardSerializer, LeaderboardSpanSerializer)
from leaderboards import service as leaderboards_service
from shows import service as shows_service
from utilities.api import APIObject


class LeaderboardEntryAPIObject(APIObject):
    field_list = ['id',
                  'user_id',
                  'username',
                  'points',
                  'wins']

    def __init__(self, leaderboard_entry, **kwargs):
        super(LeaderboardEntryAPIObject, self).__init__(leaderboard_entry, **kwargs)
        self.show = leaderboard_entry.show.id
        self.channel_name = leaderboard_entry.channel.name


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
        order_by_points = self.request.query_params.get('order_by_points')
        if user_id:
            kwargs['user'] = user_id
        if channel_id:
            kwargs['channel'] = channel_id
        if show_id:
            kwargs['show'] = show_id
        queryset = LeaderboardEntry.objects.filter(**kwargs)
        if order_by_show_date is not None:
            queryset = queryset.order_by('-show_date')
        if order_by_points is not None:
            queryset = queryset.order_by('-points')
        leaderboard_entry_list = [LeaderboardEntryAPIObject(item) for item in queryset]
        serializer = LeaderboardEntrySerializer(leaderboard_entry_list, many=True)
        return Response(serializer.data)

class LeaderboardViewSet(viewsets.ViewSet):
    """
    API endpoint for show, channel, or combined leaderboards
    """

    def fetch_leaderboard_list(self, queryset, show_id):
        user_dict = {}
        for entry in queryset:
            user_dict.setdefault(entry.user_id, {})
            user_dict[entry.user_id].setdefault('username', entry.user.username)
            user_dict[entry.user_id].setdefault('points', 0)
            user_dict[entry.user_id].setdefault('wins', 0)
            if show_id:
                user_dict[entry.user_id].setdefault('suggestions', 0)
                user_dict[entry.user_id].setdefault('medals', [])
                medal_ids = [lem.medal.id for lem in leaderboards_service.fetch_medals_by_leaderboard_entry(entry.id)]
                user_dict[entry.user_id]['medals'] = medal_ids
                user_dict[entry.user_id]['suggestions'] = shows_service.fetch_suggestion_count_by_user(
                                                            entry.user_id,
                                                            show_id=show_id)
            # Add the wins, points, medals, and suggestions for the user from this particular show
            user_dict[entry.user_id]['points'] += entry.points
            user_dict[entry.user_id]['wins'] += entry.wins
        leaderboard_list = []
        # Turn that dictionary into a list of dictionaries
        for user_id, value_dict in user_dict.items():
            user_data = {'user_id': user_id}
            user_data.update(value_dict)
            leaderboard_list.append(user_data)
        # Sort the list by points
        return sorted(leaderboard_list, key=lambda k: k['points'], reverse=True)


    def list(self, request):
        queryset = LeaderboardEntry.objects.all()
        channel_id = self.request.query_params.get('channel_id')
        show_id = self.request.query_params.get('show_id')
        if channel_id:
            queryset = queryset.filter(channel=channel_id)
        if show_id:
            queryset = queryset.filter(show=show_id)
        leaderboard_list = self.fetch_leaderboard_list(queryset, show_id)
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
            queryset.filter(channel=channel_id)
        serializer = LeaderboardSpanSerializer(queryset, many=True)
        return Response(serializer.data)


class MedalViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows medals to be viewed
    """
    model = Medal
    serializer_class = MedalSerializer
    queryset = Medal.objects.all()