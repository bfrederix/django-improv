from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from channels import service as channels_service
from channels.models import Channel
from leaderboards.models import LeaderboardEntry

class Command(BaseCommand):
    """
    How to run:

    python manage.py update_channel_users
    """
    help = 'Updates all Channel User Stats'

    def handle(self, *args, **options):
        # Loop through all channels
        for channel in Channel.objects.all():
            # Loop through all users
            for user in User.objects.all():
                # Loop through all leaderboard entries for that user
                for leaderboard_entries in LeaderboardEntry.object.filter(user_id=user.id):
                    # Update the stats for their channel user
                    channels_service.update_channel_user(channel, user, leaderboard_entries)