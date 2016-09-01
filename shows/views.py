import datetime
import logging
import pytz
import grequests

from django.conf import settings
from django.shortcuts import render
from django.http import (JsonResponse, HttpResponseRedirect, HttpResponse,
                         HttpResponseServerError, HttpResponseNotFound)
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
    logger.error("Request Failed: {0}".format(exception))


def get_show_url(url_name, host, channel_name, show_id):
    # If this is dev
    if settings.DEBUG:
        protocol = 'http'
    # This is production, use https
    else:
        protocol = 'https'
    live_vote_path = reverse(url_name,
                             kwargs={'channel_name': channel_name,
                                     'show_id': show_id})
    # return the live vote url
    return  "{0}://{1}{2}".format(protocol, host, live_vote_path)


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
        # If there isn't a show
        if not context['current_show']:
            # Do nothing
            pass
        # If we are starting a vote type
        elif vote_start:
            # Get the vote type
            vote_type = channels_service.vote_type_or_404(vote_start)
            # Start the next interval for the show for the given vote type
            view_utils.start_new_interval(context['current_show'], vote_type)
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
            # Get the current vote type
            vote_type = context['current_show'].current_vote_type
            # If we should show the option values instead of just numbers (slows things down)
            if vote_type and vote_type.show_option_values:
                vote_options = shows_service.fetch_vote_options(show_id,
                                                                vote_type.id,
                                                                vote_type.current_interval)
                context['show_option_values'] = vote_type.show_option_values
            else:
                # Get a list of the max numbered vote options
                vote_options = range(1, context['current_show'].vote_options + 1)
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
        option_value = request.POST.get('option_value')
        context = self.get_default_channel_context(request, *args, **kwargs)
        # If there's a current show
        if context['current_show']:
            # Get the current vote type
            vote_type = context['current_show'].current_vote_type
            # If we should show the option values instead of just numbers (slows things down)
            if vote_type and vote_type.show_option_values:
                vote_options = shows_service.fetch_vote_options(show_id,
                                                                vote_type.id,
                                                                vote_type.current_interval)
                context['show_option_values'] = vote_type.show_option_values
                # Get the option that the user already voted for if it exists
                voted_for = shows_service.user_voted_for(getattr(self.request.user, 'id'),
                                                         session_utils.get_or_create_session_id(request),
                                                         vote_options)
                if voted_for:
                    # Set the already voted for option value
                    option_value = voted_for
            else:
                # Get a list of the max numbered vote options
                vote_options = range(1, context['current_show'].vote_options + 1)
            # If there is a current vote type, and the vote type requires login
            if vote_type and vote_type.require_login and not getattr(request.user, 'id'):
                # Redirect the user to the login page
                redirect_url = "{0}?next={1}".format(reverse('user_login'), request.path)
                return HttpResponseRedirect(redirect_url)
        else:
            vote_options = []
        # If they chose an option
        if option_number:
            # Get the live vote url
            live_vote_url = get_show_url('show_live_vote',
                                         request.META['HTTP_HOST'],
                                         channel_name,
                                         show_id)
            # Get the vote receiver url
            vote_receiver_url = get_show_url('show_vote_receiver',
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
            #grequests.map([gpost], exception_handler=async_exception_handler)
        context.update({'show_id': int(show_id),
                        'vote_options': vote_options,
                        'option_value': option_value})
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
            user_id = int(user_id)
            # Determine if they're a channel admin
            is_channel_admin = channels_service.check_is_channel_admin(context['channel'],
                                                                       user_id)
        else:
            user = None
            is_channel_admin = False
        # If they aren't a channel admin
        if not is_channel_admin:
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
            leaderboards_service.add_leaderboard_entry_points(context['channel'],
                                                              context['current_show'],
                                                              user,
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
            # Fetch the leaderboard entries for the user
            leaderboard_entries = leaderboards_service.fetch_leaderboard_entries_by_user(user_id)
            # Add the user as a channel user and update their leaderboard aggregate stats
            channels_service.update_channel_user(context['channel'], user, leaderboard_entries)
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
                user_id = int(user_id)
            else:
                suggestion_kwargs['session_id'] = session_id
            Suggestion.objects.get_or_create(**suggestion_kwargs)
            # Don't create leaderboard entries for channel admins
            if not context['is_channel_admin']:
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
        leaderboards_service.update_leaderboard_entry_session_to_user(context['current_show'].id,
                                                                      session_id,
                                                                      user_id)
        # Fetch the leaderboard entries for the user
        leaderboard_entries = leaderboards_service.fetch_leaderboard_entries_by_user(user_id)
        # Add the user as a channel user and update their leaderboard aggregate stats
        channels_service.update_channel_user(context['channel'], self.request.user, leaderboard_entries)
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