from rest_framework import routers

#from players import api_views as players_api_views
from users import api_views as users_api_views
from shows import api_views as shows_api_views
from channels import api_views as channels_api_views
from leaderboards import api_views as leaderboards_api_views


router = routers.DefaultRouter()
# Users
router.register(r'user',
                users_api_views.UserProfileViewSet,
                'user')

# Shows
router.register(r'show',
                shows_api_views.ShowViewSet,
                'show')

# Shows
router.register(r'channel',
                channels_api_views.ChannelViewSet,
                'channel')

# Leaderboard Entries
router.register(r'leaderboard_entry',
                leaderboards_api_views.LeaderboardEntryViewSet,
                'leaderboard-entry')

# Medals
router.register(r'medal',
                leaderboards_api_views.MedalViewSet,
                'medal')

