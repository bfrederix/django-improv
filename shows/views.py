import datetime
import logging
import pytz
import grequests

from django.shortcuts import render
from django.http import (JsonResponse, HttpResponseRedirect, HttpResponse,
                         HttpResponseServerError)
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from shows.models import Suggestion, PreshowVote
from shows import service as shows_service
from channels import service as channels_service
from leaderboards import service as leaderboards_service
from utilities import sessions as session_utils
from utilities import views as view_utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def async_exception_handler(request, exception):
    logger.error("Request Failed")


def get_show_url(url_name, host, channel_name, show_id):
    live_vote_path = reverse(url_name,
                             kwargs={'channel_name': channel_name,
                                     'show_id': show_id})
    # return the live vote url
    return  "http://{0}{1}".format(host, live_vote_path)


class ShowControllerView(view_utils.ShowView):
    template_name = 'shows/show_controller.html'

    def get(self, request, *args, **kwargs):
        show_id = kwargs.get('show_id')
        context = self.get_default_channel_context(request, *args, **kwargs)
        context.update({'show_id': int(show_id)})
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        show_id = kwargs.get('show_id')
        vote_start = request.POST.get('vote_start')
        lock_toggle = request.POST.get('lock_toggle')
        context = self.get_default_channel_context(request, *args, **kwargs)
        if vote_start:
            # Get the vote type
            vote_type = channels_service.vote_type_or_404(vote_start)
            # Set the vote type's next interval start
            next_interval = channels_service.start_next_interval(show_id, vote_type)
            # Set the start of the vote type's current interval to now
            vote_type.current_vote_init = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            vote_type.save()
            # if it's a players only vote type
            if vote_type.players_only:
                suggestions = []
            # Otherwise, fetch a randomized (yet sorted) amount of suggestions
            else:
                suggestions = shows_service.fetch_randomized_suggestions(show_id,
                                                                         vote_type.suggestion_pool_id,
                                                                         vote_type.options)
            # Set the voting options
            # NOTE: Live Votes get deleted for repeateable
            shows_service.set_voting_options(context['current_show'],
                                             vote_type,
                                             next_interval,
                                             suggestions=suggestions)
            # If this isn't an interval vote and the vote type has player options
            if not vote_type.intervals and vote_type.player_options:
                # Set a random player for the vote options
                shows_service.set_show_interval_random_player(context['current_show'],
                                                              vote_type,
                                                              vote_type.current_interval)
            # Make sure the show is locked
            context['current_show'].locked = True
            # Set the show's current vote type
            context['current_show'].current_vote_type = vote_type
            context['current_show'].save()
        # If a lock toggle request was made
        elif lock_toggle:
            # If the show is locked, unlock it
            if context['current_show'].locked:
                context['current_show'].locked = False
            # If the show is unlocked, lock it
            else:
                context['current_show'].locked = True
            context['current_show'].save()

        context.update({'show_id': int(show_id)})
        return render(request,
                      self.template_name,
                      context)


class ShowDisplayView(view_utils.ShowView):
    template_name = 'shows/show_display.html'

    def get(self, request, *args, **kwargs):
        show_id = kwargs.get('show_id')
        context = self.get_default_channel_context(request, *args, **kwargs)
        context.update({'show_id': int(show_id)})
        return render(request,
                      self.template_name,
                      context)


class ShowLiveVoteView(view_utils.ShowView):
    template_name = 'shows/show_live_vote.html'

    def get(self, request, *args, **kwargs):
        show_id = kwargs.get('show_id')
        context = self.get_default_channel_context(request, *args, **kwargs)
        # If there's a current show
        if context['current_show']:
            # Get a list of the max numbered vote options
            vote_options = range(1, context['current_show'].vote_options + 1)
            # Get the current vote type
            vote_type = context['current_show'].current_vote_type
            # If there is a current vote type, and the vote type requires login
            if vote_type and vote_type.require_login and not getattr(request.user, 'id'):
                # Redirect the user to the login page
                redirect_url = "{0}?next={1}".format(reverse('user_login'), request.path)
                return HttpResponseRedirect(redirect_url)
        else:
            vote_options = []
        context.update({'show_id': int(show_id),
                        'vote_options': vote_options})
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        show_id = kwargs.get('show_id')
        channel_name = kwargs.get('channel_name')
        option_number = request.POST.get('option_number')
        context = self.get_default_channel_context(request, *args, **kwargs)
        # If there's a current show
        if context['current_show']:
            # Get a list of the max numbered vote options
            vote_options = range(1, context['current_show'].vote_options + 1)
            # Get the current vote type
            vote_type = context['current_show'].current_vote_type
            # If there is a current vote type, and the vote type requires login
            if vote_type and vote_type.require_login and not getattr(request.user, 'id'):
                # Redirect the user to the login page
                redirect_url = "{0}?next={1}".format(reverse('user_login'), request.path)
                return HttpResponseRedirect(redirect_url)
        else:
            vote_options = []
        # If they chose an option
        if option_number:
            # Get the vote receiver url
            vote_receiver_url = get_show_url('show_vote_receiver',
                                             request.META['HTTP_HOST'],
                                             channel_name,
                                             show_id)
            # Get the live vote url
            live_vote_url = get_show_url('show_live_vote',
                                         request.META['HTTP_HOST'],
                                         channel_name,
                                         show_id)
            # Set the POST data for the async vote request
            vote_post_data = {'option_number': option_number,
                              'user_id': getattr(self.request.user, 'id'),
                              'session_id': session_utils.get_or_create_session_id(request)}
            # Create an async post to the vote receiver for processing
            gpost = grequests.post(vote_receiver_url,
                                   data=vote_post_data,
                                   headers={'Referer': live_vote_url})
            # Send the post
            logger.info(grequests.map([gpost], exception_handler=async_exception_handler))
        context.update({'show_id': int(show_id),
                        'vote_options': vote_options})
        return render(request,
                      self.template_name,
                      context)


class ShowVoteReceiverView(view_utils.ShowView):

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ShowVoteReceiverView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        show_id = kwargs.get('show_id')
        channel_name = kwargs.get('channel_name')
        # Get the live vote url
        live_vote_url = get_show_url('show_live_vote',
                                     request.META['HTTP_HOST'],
                                     channel_name,
                                     show_id)
        logger.info("HERE: 1")
        # Make sure they came from the correct referrer
        if live_vote_url != request.META.get('HTTP_REFERER'):
            return HttpResponseServerError('Vote Failed')
        context = self.get_default_channel_context(request, *args, **kwargs)
        # Get the current vote state
        state = channels_service.get_current_vote_state(context['current_show'].vote_types())
        # Set the current show fields
        current_display = state.get('display', 'default')
        # If we aren't in the state of voting
        if current_display != 'voting':
            return HttpResponseServerError('Currently nothing to vote on')
        option_number = request.POST.get('option_number')
        user_id = request.POST.get('user_id')
        session_id = request.POST.get('session_id')
        # Get the user if they exist
        if user_id:
            user = User.objects.get(pk=user_id)
        else:
            user = None
        # Create a leaderboard entry if it doesn't exist
        leaderboards_service.get_or_create_leaderboard_entry(context['channel'],
                                                             context['current_show'],
                                                             user,
                                                             session_id)
        # Get the current vote type
        vote_type = context['current_show'].current_vote_type
        # Get the show interval
        show_interval = shows_service.get_show_interval(show_id,
                                                        vote_type.id,
                                                        vote_type.current_interval)
        # See if a live vote already exists
        live_vote_exists = shows_service.live_votes_exist(show_interval,
                                                          user_id,
                                                          session_id)
        # If a live vote already exists, preceed no further
        if live_vote_exists:
            return HttpResponse('Already Voted')
        # If the vote type is logged in users only and the user isn't logged in
        if vote_type.require_login and not user:
            return HttpResponseServerError("You must be logged in to vote")
        # Get the vote option
        vote_option = shows_service.fetch_option(show_id,
                                                 vote_type.id,
                                                 vote_type.current_interval,
                                                 option_number)
        # Create the live vote(s)
        shows_service.create_live_votes(vote_option, show_interval, user, session_id, vote_type.require_login)

        # If it has a suggestion and it's not repeatable suggestions
        # create/update the leaderboard entry
        if vote_option.suggestion_id and not vote_type.keep_suggestions:
            # Get the suggestion from the vote option
            suggestion = vote_option.suggestion
            # Create/update leaderboard entry
            # NOTE: ChannelUser data gets updated as part of the LeaderboardEntry save method
            leaderboards_service.add_leaderboard_entry_points(context['channel'],
                                                              context['current_show'],
                                                              suggestion.user,
                                                              suggestion.session_id,
                                                              vote_type.require_login)
            # If the user is authenticated, add their user id to their suggestions
            # (remove the session id too)
            shows_service.update_suggestions_session_to_user(context['current_show'].id,
                                                             session_id,
                                                             user_id)
            # If the user is authenticated, add their user id to their leaderboard entry
            # (remove the session id too)
            leaderboards_service.update_leaderboard_entry_session_to_user(context['current_show'].id,
                                                                          session_id,
                                                                          user_id)
        return HttpResponse('Vote Received')


class ShowSuggestionPoolView(view_utils.ShowView):
    template_name = 'shows/show_suggestion_pool.html'

    def pool_auth_acceptable(self, suggestion_pool, request, context):
        """
        If login is required and the user isn't logged in
        OR if the pool is admin only and the user isn't an admin
        Return False, otherwise return True

        :param suggestion_pool:
        :param request:
        :param context:
        :return bool:
        """
        if suggestion_pool.require_login and not request.user.is_authenticated \
            or suggestion_pool.admin_only and not context['is_channel_admin']:
            return False
        return True

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        session_id = session_utils.get_or_create_session_id(request)
        # Get the Suggestion pool
        suggestion_pool_id = kwargs.get('suggestion_pool_id')
        suggestion_pool = channels_service.suggestion_pool_or_404(suggestion_pool_id)
        # Make sure the user is authenticated properly for the pool
        if not self.pool_auth_acceptable(suggestion_pool, request, context):
            # Redirect the user to the login page
            redirect_url = "{0}?next={1}".format(reverse('user_login'), request.path)
            return HttpResponseRedirect(redirect_url)
        # Determine if the user has reached the max suggestions
        disabled = shows_service.suggestions_maxed(context['current_show'],
                                                   suggestion_pool,
                                                   user_id=getattr(self.request.user, 'id'),
                                                   session_id=session_id)

        context.update({'suggestion_pool': suggestion_pool,
                        'session_id': session_id,
                        'disabled': disabled})
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        action = None
        error = None
        user_id = getattr(self.request.user, 'id')
        delete_id = request.POST.get('delete_id')
        suggestion_value = request.POST.get('suggestion_value')
        context = self.get_default_channel_context(request, *args, **kwargs)
        session_id = session_utils.get_or_create_session_id(request)
        # Get the Suggestion pool
        suggestion_pool_id = kwargs.get('suggestion_pool_id')
        suggestion_pool = channels_service.suggestion_pool_or_404(suggestion_pool_id)
        # Make sure the user is authenticated properly for the pool
        # i.e. require_login or admin_only
        if not self.pool_auth_acceptable(suggestion_pool, request, context):
            # Redirect the user to the login page
            redirect_url = "{0}?next={1}".format(reverse('user_login'), request.path)
            return HttpResponseRedirect(redirect_url)
        # If we are deleting a suggestion
        if delete_id:
            try:
                suggestion = Suggestion.objects.get(pk=delete_id)
            except ObjectDoesNotExist:
                error = "Suggestion already deleted!"
            else:
                # Make sure the user has privileges to delete the suggestion
                # Either they're an admin, or a user matching the user id or session id
                if context['is_channel_admin'] or \
                    suggestion.user_id and suggestion.user_id == user_id or \
                    suggestion.session_id == session_id:
                    # Delete the suggestion
                    suggestion.delete()
        # Add the new suggestion
        elif suggestion_value and not Suggestion.objects.filter(show=context['current_show'],
                                                                value=suggestion_value):
            suggestion_kwargs = {'channel': context['channel'],
                                 'show': context['current_show'],
                                 'suggestion_pool': suggestion_pool,
                                 'used': False,
                                 'voted_on': False,
                                 'amount_voted_on': 0,
                                 'value': suggestion_value,
                                 'preshow_value': 0,
                                 'user': None,
                                 'session_id': None,
                                 'created': datetime.datetime.utcnow().replace(tzinfo=pytz.utc)}
            if user_id:
                suggestion_kwargs['user'] = request.user
            else:
                suggestion_kwargs['session_id'] = session_id
            Suggestion.objects.get_or_create(**suggestion_kwargs)
            # Create a leaderboard entry if it doesn't exist
            leaderboards_service.get_or_create_leaderboard_entry(context['channel'],
                                                                 context['current_show'],
                                                                 suggestion_kwargs['user'],
                                                                 session_id)
        # If the superuser needs to make a bunch of suggestions
        elif request.user and request.user.is_superuser and request.POST.get('suggestalot'):
            suggestion_kwargs = {'channel': context['channel'],
                                 'show': context['current_show'],
                                 'suggestion_pool': suggestion_pool,
                                 'used': False,
                                 'voted_on': False,
                                 'amount_voted_on': 0,
                                 'user': request.user,
                                 'preshow_value': 0,
                                 'created': datetime.datetime.utcnow().replace(tzinfo=pytz.utc)}
            for i in range(1, 51):
                suggestion_kwargs['value'] = "Suggestion-{0}".format(i)
                Suggestion.objects.get_or_create(**suggestion_kwargs)
        elif suggestion_value:
            error = "Suggestion already exists!"
        else:
            error = "Suggestions cannot be blank!"
        # Determine if the user has reached the max suggestions
        disabled = shows_service.suggestions_maxed(context['current_show'],
                                                   suggestion_pool,
                                                   user_id=user_id,
                                                   session_id=session_id)
        # If the user is authenticated, add their user id to their suggestions
        # (remove the session id too)
        shows_service.update_suggestions_session_to_user(context['current_show'].id,
                                                         session_id,
                                                         user_id)
        # If the user is authenticated, add their user id to their leaderboard entry
        # (remove the session id too)
        # NOTE: ChannelUser gets implicitly updated here as part of the LeaderboardEntry save method
        leaderboards_service.update_leaderboard_entry_session_to_user(context['current_show'].id,
                                                                      session_id,
                                                                      user_id)
        context.update({'action': action,
                        'error': error,
                        'suggestion_pool': suggestion_pool,
                        'session_id': session_id,
                        'disabled': disabled})
        return render(request,
                      self.template_name,
                      context)


class UpvoteSubmitView(view_utils.ShowView):

    def post(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        suggestion_id = request.POST.get('id')
        # If a suggestion was submitted properly
        if suggestion_id:
            preshow_kwargs = {'show': context['current_show'],
                              'suggestion': Suggestion.objects.get(pk=suggestion_id),
                              'session_id': session_utils.get_or_create_session_id(request)}
            # If the user is logged in
            if getattr(self.request.user, 'id'):
                preshow_kwargs['user'] = User.objects.get(pk=request.user.id)
            # Get or create the preshow vote
            PreshowVote.objects.get_or_create(**preshow_kwargs)
        return JsonResponse({})