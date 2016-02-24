import logging

from rest_framework import viewsets
from rest_framework.response import Response

from users import service as users_service
from leaderboards import service as leaderboards_service
from shows import service as shows_service
from users.models import UserProfile
from users.serializers import UserProfileSerializer, UsernameSerializer
from utilities.api import APIObject

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserAPIObject(APIObject):
    field_list = ['user_id',
                  'safe_username',
                  'created',
                  'site_email_opt_in',
                  'channels_email_opt_in']

    def __init__(self, user_profile, **kwargs):
        super(UserAPIObject, self).__init__(user_profile, **kwargs)
        self.suggestions = shows_service.fetch_suggestions(user_id=self.user_id, count=True)
        leaderboard_entries = leaderboards_service.fetch_leaderboard_entries_by_user(
                                    self.user_id)
        self.points = 0
        self.wins = 0
        self.medals = []
        for leaderboard_entry in leaderboard_entries:
            self.points += leaderboard_entry.points
            self.wins += leaderboard_entry.wins
            self.medals = leaderboards_service.fetch_medal_ids_by_leaderboard_entry(leaderboard_entry.id)


class UserProfileViewSet(viewsets.ViewSet):
    """
    API endpoint that allows voteprov users to be viewed or edited.
    """

    def retrieve(self, request, pk=None):
        user_profile = users_service.user_profile_or_404(pk)
        user_api_obj = UserAPIObject(user_profile)
        serializer = UserProfileSerializer(user_api_obj)
        return Response(serializer.data)

    def list(self, request):
        queryset = UserProfile.objects.all()
        serializer = UserProfileSerializer(queryset, many=True)
        return Response(serializer.data)


class UsernameViewSet(viewsets.ViewSet):
    """
    API endpoint that gets a list of users by a query value
    """

    def list(self, request):
        query = self.request.query_params.get('q', '').lower()
        queryset = UserProfile.objects.filter(strip_username__contains=query)[:10]
        return Response([q.username for q in queryset])