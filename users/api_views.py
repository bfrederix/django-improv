from users.models import UserProfile
from rest_framework import viewsets
from users.serializers import UserProfileSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows voteprov users to be viewed or edited.
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer