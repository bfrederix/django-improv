from rest_framework import serializers


class UserProfileSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField(source='safe_username')
    created = serializers.DateTimeField()
    site_email_opt_in = serializers.BooleanField()
    points = serializers.IntegerField()
    wins = serializers.IntegerField()
    suggestions = serializers.IntegerField()
    medals = serializers.ListField()

    class Meta:
        fields = ('user_id', 'username', 'created',
                  'site_email_opt_in',
                  'points', 'wins', 'suggestions', 'medals',)


class UsernameSerializer(serializers.Serializer):
    pass