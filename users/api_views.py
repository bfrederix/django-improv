from rest_framework import viewsets
from rest_framework.response import Response

from users import service as users_service
from leaderboards import service as leaderboards_service
from shows import service as shows_service
from users.models import UserProfile
from users.serializers import UserProfileSerializer
from utilities.api import APIObject


class UserAPIObject(APIObject):
    field_list = ['user_id',
                  'safe_username',
                  'created',
                  'site_email_opt_in',
                  'channels_email_opt_in']

    def __init__(self, user_profile, **kwargs):
        super(UserAPIObject, self).__init__(user_profile, **kwargs)
        self.suggestions = shows_service.fetch_suggestion_count_by_user(self.user_id)
        leaderboard_entries = leaderboards_service.fetch_leaderboard_entries_by_user(
                                    self.user_id)
        self.points = 0
        self.wins = 0
        self.medals = []
        for leaderboard_entry in leaderboard_entries:
            self.points += leaderboard_entry.points
            self.wins += leaderboard_entry.wins
            #import pdb; pdb.set_trace()
            medals = leaderboards_service.fetch_medals_by_leaderboard_entry(leaderboard_entry.id)
            self.medals += [medal.medal.id for medal in medals]


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
