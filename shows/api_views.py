import datetime
import pytz

from rest_framework import viewsets
from rest_framework.response import Response

from shows.models import Show, Suggestion, LiveVote, PreshowVote
from shows.serializers import (ShowSerializer, SuggestionsSerializer,
                               VoteOptionSerializer, LiveVoteSerializer)
from shows import service as shows_service
from channels import service as channels_service
from users import service as users_service
from leaderboards import service as leaderboards_service
from utilities.api import APIObject


class ShowAPIObject(APIObject):
    field_list = ['id',
                  'created',
                  'locked',
                  'show_length',
                  'photo_link',
                  'embedded_youtube',
                  'formatted_youtube',
                  'formatted_date',
                  'show_end',
                  'vote_types',
                  'show_seconds_remaining']

    def __init__(self, show, **kwargs):
        super(ShowAPIObject, self).__init__(show, **kwargs)
        self.channel_id = show.channel_id
        self.channel_name = show.channel.name
        current_show = shows_service.get_current_show(self.channel_id)
        # If the Show is the current running show
        if show.id == getattr(current_show, 'id', None):
            self.running = True
            # Get the current vote state
            state = channels_service.get_current_vote_state(show.vote_types())
            # Set the current show fields
            self.current_display = state.get('display', 'default')
            self.current_vote_type = state.get('vote_type_id', None)

            # If we're in the voting state
            if self.current_display == 'voting':
                # Gets the vote type and current player if they exist
                self.set_default_vote_data(show.id)
                # Get the vote options for this (interval or not)
                self.vote_options = shows_service.fetch_vote_option_ids(
                                                                show_id=show.id,
                                                                vote_type_id=self.vote_type.id,
                                                                interval=self.vote_type.current_interval)
            # If we're in the result state
            elif self.current_display == 'result':
                # Gets the vote type and current player if they exist
                self.set_default_vote_data(show.id)
                # Gets the current VotedItem
                current_voted = shows_service.get_current_voted(show.id,
                                                                self.vote_type.id,
                                                                self.vote_type.current_interval)
                # If we haven't established a voted option
                if not current_voted:
                    # Get the vote options for this (interval or not)
                    vote_options = shows_service.fetch_vote_options(show_id=show.id,
                                                                    vote_type_id=self.vote_type.id,
                                                                    interval=self.vote_type.current_interval)
                    # Determine the winning option
                    winning_option = shows_service.get_winning_option(self.vote_type,
                                                                      vote_options)
                    # If there is a winner
                    if winning_option:
                        # Set the voted winning option
                        shows_service.set_voted_option(show,
                                                       self.vote_type,
                                                       self.vote_type.current_interval,
                                                       winning_option)
                    # If the winning option was a user submitted suggestion
                    if winning_option.suggestion_id:
                        # Add a suggestion win to the leaderboard entry
                        leaderboards_service.add_leaderboard_entry_win(show.id,
                                                                       winning_option.suggestion.user_id,
                                                                       winning_option.suggestion.session_id)
        # Otherwise this show isn't currently running
        else:
            self.running = False

    def set_default_vote_data(self, show_id):
        self.vote_type = channels_service.vote_type_or_404(self.current_vote_type)
        # Get the current show interval
        show_interval = shows_service.get_show_interval(show_id,
                                                        self.vote_type.id,
                                                        self.vote_type.current_interval)
        # If one exists
        if show_interval:
            # Get the player for that interval
            self.current_player = show_interval.player_id


class SuggestionAPIObject(APIObject):
    field_list = ['id',
                  'created',
                  'used',
                  'voted_on',
                  'value',
                  'preshow_value',
                  'session_id']

    def __init__(self, suggestion, **kwargs):
        super(SuggestionAPIObject, self).__init__(suggestion, **kwargs)
        self.user_id = getattr(suggestion, 'user_id', None)
        upvote_user_id = kwargs.get('upvote_user_id')
        upvote_session_id = kwargs.get('upvote_session_id')
        if upvote_user_id and upvote_user_id !="None":
            self.user_already_upvoted = bool(PreshowVote.objects.filter(show=suggestion.show_id,
                                                                        suggestion=suggestion,
                                                                        user=upvote_user_id).count())
        elif upvote_session_id and upvote_session_id !="None":
            self.user_already_upvoted = bool(PreshowVote.objects.filter(show=suggestion.show_id,
                                                                        suggestion=suggestion,
                                                                        session_id=upvote_session_id).count())
        else:
            self.user_already_upvoted = False


class VoteOptionAPIObject(APIObject):
    field_list = ['id',
                  'option_number',
                  'show_id',
                  'vote_type_id',
                  'interval']

    def __init__(self, option, **kwargs):
        super(VoteOptionAPIObject, self).__init__(option, **kwargs)
        self.player_id = option.player_id
        self.suggestion_id = option.suggestion_id
        # Determine if we should show the vote count
        self.hide_display_vote_count = option.vote_type.hide_display_vote_count
        self.hide_recap_vote_count = option.vote_type.hide_recap_vote_count
        self.show_option_values = option.vote_type.show_option_values
        # If there was a suggestion for the option
        if option.suggestion_id:
            suggestion = option.suggestion
            self.used = suggestion.used
            self.suggestion_value = suggestion.value
            user_id = suggestion.user_id
            if user_id:
                user_profile = users_service.fetch_user_profile(user_id)
                self.user_id = user_profile.user_id
                self.username = user_profile.safe_username
                self.user_wins = shows_service.show_user_winning_suggestion_count(suggestion.show_id,
                                                                                  user_id)
        # If there was a player for the option
        if option.player_id:
            self.player_name = option.player.name
            self.player_photo = option.player.photo_url
        # Get the live votes for all the current vote options
        current_vote_options = shows_service.fetch_vote_options(show_id=option.show_id,
                                                                vote_type_id=option.vote_type_id,
                                                                interval=option.interval)
        self.vote_options_count = len(current_vote_options)
        self.min_votes = 0
        self.max_votes = 0
        for vote_option in current_vote_options:
            # Get the live votes for this option
            live_votes = shows_service.get_option_live_votes(vote_option.id)
            # If we haven't established a min count
            if self.min_votes == 0:
                self.min_votes = live_votes
            # If this option's live votes are less than the current minimum votes
            if live_votes < self.min_votes:
                self.min_votes = live_votes
            # If this option's live votes are greater than the current maximum votes
            if live_votes > self.max_votes:
                self.max_votes = live_votes
            # If this is the option requested
            if vote_option.id == option.id:
                # Set its live votes to be returned by the api
                self.live_votes = live_votes

class ShowViewSet(viewsets.ViewSet):
    """
    API endpoint that allows shows to be viewed
    """

    def retrieve(self, request, pk=None):
        show = shows_service.show_or_404(pk)
        show_api_obj = ShowAPIObject(show)
        serializer = ShowSerializer(show_api_obj)
        return Response(serializer.data)

    def list(self, request):
        kwargs = {}
        channel_id = self.request.query_params.get('channel_id')
        order_by_date = self.request.query_params.get('order_by_date')
        # Filtering
        if channel_id:
            kwargs['channel'] = channel_id
        queryset = Show.objects.filter(**kwargs)
        # Ordering
        if order_by_date:
            queryset = queryset.order_by('-created')
        updated_shows = [ShowAPIObject(item) for item in queryset]
        serializer = ShowSerializer(updated_shows, many=True)
        return Response(serializer.data)


class SuggestionViewSet(viewsets.ViewSet):
    """
    API endpoint that allows suggestions to be viewed
    """

    def retrieve(self, request, pk=None):
        suggestion = shows_service.suggestion_or_404(pk)
        suggestion_api_obj = SuggestionAPIObject(suggestion)
        serializer = SuggestionsSerializer(suggestion_api_obj)
        return Response(serializer.data)

    def list(self, request):
        kwargs = {}
        api_kwargs = {'upvote_user_id': self.request.query_params.get('upvote_user_id'),
                      'upvote_session_id': self.request.query_params.get('upvote_session_id')}
        user_id = self.request.query_params.get('user_id')
        show_id = self.request.query_params.get('show_id')
        suggestion_pool_id = self.request.query_params.get('suggestion_pool_id')
        suggestion_pool_sort = self.request.query_params.get('suggestion_pool_sort')
        if user_id:
            kwargs['user'] = user_id
        if show_id:
            kwargs['show'] = show_id
        if suggestion_pool_id:
            kwargs['suggestion_pool'] = suggestion_pool_id
        queryset = Suggestion.objects.filter(**kwargs)
        # If we need to sort the suggestions for a suggestion pool display
        if suggestion_pool_sort:
            queryset = queryset.order_by('-preshow_value', 'created')
        updated_suggestions = [SuggestionAPIObject(item, **api_kwargs) for item in queryset]
        serializer = SuggestionsSerializer(updated_suggestions, many=True)
        return Response(serializer.data)


class VoteOptionViewSet(viewsets.ViewSet):
    """
    API endpoint that returns leaderboard entries
    """

    def retrieve(self, request, pk=None):
        vote_option = shows_service.get_option(pk)
        serializer = VoteOptionSerializer(VoteOptionAPIObject(vote_option))
        return Response(serializer.data)

    def list(self, request):
        ### DO NOT DELETE, WE NEED THIS FOR THE API URL ###
        pass


class LiveVoteViewSet(viewsets.ViewSet):
    """
    API endpoint that allows live votes to be viewed
    """

    def list(self, request):
        kwargs = {}
        vote_option_id = self.request.query_params.get('vote_option_id')
        if vote_option_id:
            kwargs['vote_option'] = vote_option_id
        count = LiveVote.objects.filter(**kwargs).count()
        serializer = LiveVoteSerializer({'count': count})
        return Response(serializer.data)