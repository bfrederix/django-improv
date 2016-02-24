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

# Usernames
router.register(r'username',
                users_api_views.UsernameViewSet,
                'username')

# Shows
router.register(r'show',
                shows_api_views.ShowViewSet,
                'show')

# Channels
router.register(r'channel',
                channels_api_views.ChannelViewSet,
                'channel')

# Channel Addresses
router.register(r'channel_address',
                channels_api_views.ChannelAddressViewSet,
                'channel-address')

# Channel Names
router.register(r'channel_name',
                channels_api_views.ChannelNameViewSet,
                'channel-name')

# Player
router.register(r'player',
                players_api_views.PlayerViewSet,
                'player')

# Suggestion Pool
router.register(r'suggestion_pool',
                channels_api_views.SuggestionPoolViewSet,
                'suggestion-pool')

# Vote Type
router.register(r'vote_type',
                channels_api_views.VoteTypeViewSet,
                'vote-type')

# Vote Styles
router.register(r'vote_style',
                channels_api_views.VoteStyleViewSet,
                'vote-style')

# Suggestions
router.register(r'suggestion',
                shows_api_views.SuggestionViewSet,
                'suggestion')

# Vote Options
router.register(r'vote_option',
                shows_api_views.VoteOptionViewSet,
                'vote-option')

# Live Votes
router.register(r'live_vote',
                shows_api_views.LiveVoteViewSet,
                'live-vote')

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

# Leaderboard Spans
router.register(r'leaderboard_span',
                leaderboards_api_views.LeaderboardSpanViewSet,
                'leaderboard-span')

# Medals
router.register(r'medal',
                leaderboards_api_views.MedalViewSet,
                'medal')

