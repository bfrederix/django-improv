from rest_framework import routers

from players import api_views as players_api_views
from users import api_views as users_api_views
from shows import api_views as shows_api_views
from channels import api_views as channels_api_views
from leaderboards import api_views as leaderboards_api_views
from recaps import api_views as recaps_api_views


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

# Player
router.register(r'player',
                players_api_views.PlayerViewSet,
                'player')

# Suggestions
router.register(r'suggestion',
                shows_api_views.SuggestionViewSet,
                'suggestion')

# Leaderboard Entries
router.register(r'leaderboard_entry',
                leaderboards_api_views.LeaderboardEntryViewSet,
                'leaderboard-entry')

# Leaderboards
router.register(r'leaderboard',
                leaderboards_api_views.LeaderboardViewSet,
                'leaderboard')

# Recaps
router.register(r'recap',
                recaps_api_views.RecapViewSet,
                'recap')

# Vote Options
router.register(r'vote_option',
                recaps_api_views.VoteOptionsViewSet,
                'vote-option')

# Leaderboard Spans
router.register(r'leaderboard_span',
                leaderboards_api_views.LeaderboardSpanViewSet,
                'leaderboard-span')

# Medals
router.register(r'medal',
                leaderboards_api_views.MedalViewSet,
                'medal')

