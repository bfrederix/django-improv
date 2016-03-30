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
                # Update the stats for their channel user
                channels_service.update_channel_user(
                    channel,
                    user,
                    LeaderboardEntry.objects.filter(user_id=user.id))
                print("Updated user: {0}".format(user.id))