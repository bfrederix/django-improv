import datetime
import re
import csv
import logging
import pytz
import StringIO
import cloudinary.uploader

from django.shortcuts import render, redirect
from django.utils.html import escape, strip_tags
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib.sitemaps import ping_google

from channels.models import (Channel, ChannelAddress, ChannelOwner,
                             ChannelAdmin, SuggestionPool, VoteType)
from channels import service as channels_service
from players import service as players_service
from shows import service as shows_service
from users import service as users_service
from leaderboards import service as leaderboards_service
from utilities import views as view_utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def name_validator(channel, name):
    # If it's an invalid name
    if not re.match('[0-9a-z-]', name):
        return "Invalid Channel Name"
    # If the channel already exists and doesn't have the exact same name
    if channel and channel.name != name:
        # See if the name has been used already
        try:
            Channel.objects.get(name__iexact=name)
        except ObjectDoesNotExist:
            return None
        else:
            return "Channel Name already taken"
    return None


class ChannelHomeView(view_utils.ShowView):
    template_name = 'channels/channel_home.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        return render(request,
                      self.template_name,
                      context)


class ChannelBrowseView(view_utils.ShowView):
    template_name = 'channels/channels_browse.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        context.update(
            {'channels': channels_service.fetch_channels()})
        return render(request,
                      self.template_name,
                      context)


class ChannelCreateEditView(view_utils.ShowView):
    template_name = 'channels/channel_create_edit.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        action = None
        channel_id = kwargs.get('channel_id')
        delete = request.POST.get('delete')
        context = self.get_default_channel_context(request, *args, **kwargs)
        # If we're deleting the channel
        if delete:
            # Archive it
            context['channel'].archived = True
            context['channel'].save()
            # redirect to the home
            return redirect('dumpedit_home')
        # If we're editing the channel
        elif channel_id:
            action = "Channel Edited Successfully!"

        error = name_validator(context['channel'], request.POST.get('name'))
        next_show = request.POST.get('next_show')
        # If a next show was submitted
        if next_show:
            next_show = datetime.datetime.strptime(next_show, "%Y-%m-%d %H:%M").replace(tzinfo=pytz.utc)
        else:
            next_show = None
        channel_update = {"name": request.POST.get('name'),
                          "display_name": request.POST.get('display_name'),
                          "email": request.POST.get('email'),
                          "short_description": strip_tags(request.POST.get('short_description', '')),
                          "description": strip_tags(request.POST.get('description', '')),
                          "website": strip_tags(request.POST.get('website', '')),
                          "facebook_page": strip_tags(request.POST.get('facebook_page', '')),
                          "buy_tickets_link": strip_tags(request.POST.get('buy_tickets_link', '')),
                          "next_show": next_show,
                          "navbar_color": request.POST.get('navbar_color'),
                          "background_color": request.POST.get('background_color')}
        address_update = {"street": request.POST.get('street'),
                          "city": request.POST.get('city'),
                          "state": request.POST.get('state'),
                          "zipcode": request.POST.get('zipcode')}
        image_update = {"team_photo_url": request.FILES.get('teamPhotoFile')}
        # E-mail is required for the channel
        if not channel_update['email'] or not channel_update['display_name']:
            error = "Url Name, Display Name, and Contact Email are all required."
        # If this channel doesn't already exist (and there's no errors)
        elif not context['channel'] and not error:
            context['channel'] = Channel(**channel_update)
            context['channel'].created = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        # Otherwise the channel exists (and there's no errors)
        elif not error:
            for field, value in channel_update.items():
                setattr(context['channel'], field, value)
        # If there wasn't an error, save the channel
        if not error:
            context['channel'].save()
            # Tell google to update from the sitemap
            try:
                ping_google()
            except Exception:
                # Bare 'except' because we could get a variety
                # of HTTP-related exceptions.
                pass
        # Update or create images in cloudinary
        for field_name, img_file in image_update.items():
            if img_file and not error:
                public_id = "{0}_{1}".format(field_name, context['channel'].id)
                cloud_response = cloudinary.uploader.upload(img_file,
                                                            folder="channels",
                                                            public_id=public_id,
                                                            invalidate=True)
                setattr(context['channel'], field_name, cloud_response.get('secure_url'))
        # If there were no errors, save the channel
        if not error:
            # Create/Update the channel address
            if not context['channel'].address:
                channel_address = ChannelAddress(**address_update)
                channel_address.save()
                context['channel'].address = channel_address
            else:
                for field, value in address_update.items():
                    setattr(context['channel'].address, field, value)
                context['channel'].address.save()
            context['channel'].save()
            # If this is a new channel
            if not channel_id:
                context['channel'].created = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
                context['channel'].save()
                # Make the current user the owner and admin of the channel
                ChannelOwner.objects.get_or_create(channel=context['channel'],
                                                   user=request.user)
                ChannelAdmin.objects.get_or_create(channel=context['channel'],
                                                   user=request.user)
                # redirect to the newly created channel
                return redirect('channel_home', channel_name=context['channel'].name)

        context.update(
            {'action': action,
             'error': error})
        return render(request,
                      self.template_name,
                      context)


class ChannelPlayersView(view_utils.ShowView):
    template_name = 'channels/channel_players.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        error = None
        action = None
        player_id = request.POST.get('playerID')
        delete = request.POST.get('delete')
        player_name = escape(request.POST.get('player_name', ''))
        active = bool(request.POST.get('active', False))
        star = bool(request.POST.get('star', False))
        # If we're deleting the player
        if delete:
            action = "Player Deleted Successfully!"
            player = players_service.player_or_404(delete)
            # Archive the player
            player.archived = True
        # If we're editing the player
        elif player_id and player_name:
            action = "Player Edited Successfully!"
            player = players_service.player_or_404(player_id)
            player.name = player_name
            player.active = active
            player.star = star
        # If we're creating the player
        elif player_name:
            action = "Player Created Successfully!"
            player = players_service.create_player(player_name,
                                                   context['channel'],
                                                   "temp",
                                                   active=active,
                                                   star=star)
        else:
            error = 'Player name required'
        # Update or create the player image in cloudinary
        uploaded_file = request.FILES.get('file')
        # Files larger than 2MB won't appear in request.FILES
        if uploaded_file and not error and not delete:
            cloud_response = cloudinary.uploader.upload(uploaded_file,
                                                        folder="players",
                                                        public_id=player.id,
                                                        invalidate=True)
            player.photo_url = cloud_response.get('secure_url')
        # If there were no errors, save the player
        if not error and not delete:
            player.save()

        context.update(
            {'action': action,
             'error': error})
        return render(request,
                      self.template_name,
                      context)


class ChannelSuggestionPoolsView(view_utils.ShowView):
    template_name = 'channels/channel_suggestion_pools.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        error = None
        action = None
        suggestion_pool_id = request.POST.get('selectID')
        delete = request.POST.get('delete')
        suggestion_pool_kwargs = {'channel': context['channel'],
                                  'name': escape(request.POST.get('name', '')),
                                  'display_name': escape(request.POST.get('display_name', '')),
                                  'description': strip_tags(request.POST.get('description', '')),
                                  'max_user_suggestions': int(request.POST.get('max_user_suggestions', 5)),
                                  'require_login': bool(request.POST.get('require_login', False)),
                                  'active': bool(request.POST.get('active', False)),
                                  'admin_only': bool(request.POST.get('admin_only', False))}
        # If we're deleting the suggestion pool
        if delete:
            action = "Suggestion Pool Deleted Successfully!"
            suggestion_pool = channels_service.suggestion_pool_or_404(delete)
            # Archive the suggestion pool
            suggestion_pool.archived = True
        # If we're editing the suggestion pool
        elif suggestion_pool_id and suggestion_pool_kwargs['name']:
            action = "Suggestion Pool Edited Successfully!"
            suggestion_pool = channels_service.suggestion_pool_or_404(suggestion_pool_id)
            for key, value in suggestion_pool_kwargs.items():
                setattr(suggestion_pool, key, value)
        # If we're creating the suggestion pool
        elif suggestion_pool_kwargs['name']:
            action = "Suggestion Pool Created Successfully!"
            suggestion_pool = SuggestionPool(**suggestion_pool_kwargs)
            suggestion_pool.created = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        else:
            error = 'Suggestion Pool name required'

        if not error and not delete:
            suggestion_pool.save()

        context.update(
            {'action': action,
             'error': error})
        return render(request,
                      self.template_name,
                      context)


class ChannelVoteTypesView(view_utils.ShowView):
    template_name = 'channels/channel_vote_types.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        error = None
        action = None
        vote_type_id = request.POST.get('selectID')
        delete = request.POST.get('delete')
        suggestion_pool_id = request.POST.get('suggestion_pool', 0)
        # If a suggestion pool was selected (and not 0)
        if suggestion_pool_id:
            suggestion_pool = SuggestionPool.objects.get(pk=int(suggestion_pool_id))
        # Otherwise set no suggestion pool
        else:
            suggestion_pool = None
        # We don't need these if we're deleting
        if not delete:
            vote_type_kwargs = {'channel': context['channel'],
                                'name': escape(request.POST.get('name', '')),
                                'display_name': escape(request.POST.get('display_name', '')),
                                'suggestion_pool': suggestion_pool,
                                'intervals': request.POST.get('intervals', '').strip(),
                                'preshow_selected': bool(request.POST.get('preshow_selected', False)),
                                'manual_interval_control': bool(request.POST.get('manual_interval_control', False)),
                                'style': channels_service.vote_style_or_404(int(request.POST.get('style')))[0],
                                'ordering': int(request.POST.get('ordering', 0)),
                                'options': int(request.POST.get('options', 3)),
                                'vote_length': int(request.POST.get('vote_length', 25)),
                                'result_length': int(request.POST.get('result_length', 10)),
                                'button_color': request.POST.get('button_color'),
                                'require_login': bool(request.POST.get('require_login', False)),
                                'active': bool(request.POST.get('active', False))}
            vote_type_kwargs.update(
                channels_service.vote_type_style_to_fields(vote_type_kwargs['style']))
        # If we're deleting the vote type
        if delete:
            action = "Vote Type Deleted Successfully!"
            vote_type = channels_service.vote_type_or_404(delete)
            # Archive the vote type
            vote_type.archived = True
        # If we are editing and the required name and style are met
        elif vote_type_id and vote_type_kwargs['name'] and vote_type_kwargs['style']:
            action = "Vote Type Edited Successfully!"
            vote_type = channels_service.vote_type_or_404(vote_type_id)
            for key, value in vote_type_kwargs.items():
                setattr(vote_type, key, value)
        # If we are creating and the required name and style are met
        elif vote_type_kwargs['name'] and vote_type_kwargs['style']:
            action = "Vote Type Created Successfully!"
            vote_type = VoteType(**vote_type_kwargs)
            vote_type.created = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        # name and style are REQUIRED
        else:
            error = 'Vote Type Name and Style required'

        if not error and not delete:
            vote_type.save()

        context.update(
            {'action': action,
             'error': error})
        return render(request,
                      self.template_name,
                      context)


class ChannelShowsView(view_utils.ShowView):
    template_name = 'channels/channel_shows.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        error = None
        action = None
        show_id = request.POST.get('selectID')
        delete = request.POST.get('delete')
        # If we're deleting a show
        if delete:
            show = shows_service.show_or_404(delete)
            show.delete()
            action = "Show Deleted Successfully!"
        # If we're updating a show
        elif show_id:
            show = shows_service.show_or_404(show_id)
            action = "Show Updated Successfully!"
        # Otherwise we're creating a new show
        else:
            player_ids = request.POST.getlist('players')
            vote_type_ids = request.POST.getlist('vote_types')
            # Get the vote types selected
            vote_types = channels_service.fetch_vote_types_by_ids(vote_type_ids)
            # If players were selected, fetch them
            if player_ids:
                players = players_service.fetch_players_by_ids(player_ids, star=False)
                # Get the star players
                star_players = players_service.fetch_players_by_ids(player_ids, star=True)
                # Get both star and regular players
                combined_players = players_service.fetch_players_by_ids(player_ids)
            # Otherwise the show has no players
            else:
                players = []
                star_players = []
                combined_players = []
            show = shows_service.create_show(context['channel'],
                                             vote_types,
                                             request.POST.get('show_length', 180),
                                             players=players,
                                             star_players=star_players,
                                             combined_players=combined_players)
            action = "Show Created Successfully!"
            # Update the context after creating the show
            context = self.get_default_channel_context(request, *args, **kwargs)
        # If we're not deleting the show
        if not delete:
            show.embedded_youtube = shows_service.validate_youtube(
                                        request.POST.get('embedded_youtube', ''))
            # Update or create the show image in cloudinary
            uploaded_file = request.FILES.get('photoFile')
            # Files larger than 2MB won't appear in request.FILES
            if uploaded_file and not error:
                cloud_response = cloudinary.uploader.upload(uploaded_file,
                                                            folder="shows",
                                                            public_id=show.id,
                                                            invalidate=True)
                show.photo_link = cloud_response.get('secure_url')
            # update the show length
            show.show_length = request.POST.get('show_length')

            if not error:
                show.save()
        # If we've created a new show
        if not delete and not show_id:
            return redirect('show_controller',
                            channel_name=context['channel'].name,
                            show_id=show.id)
        # Make sure to update the current show in context
        context.update(
            {'current_show': shows_service.get_current_show(context['channel'].id),
             'action': action,
             'error': error})
        return render(request,
                      self.template_name,
                      context)


class ChannelPreShowView(view_utils.ShowView):
    template_name = 'channels/channel_pre_show.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        return render(request,
                      self.template_name,
                      context)


class ChannelLeaderboardSpansView(view_utils.ShowView):
    template_name = 'channels/channel_leaderboard_spans.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        error = None
        action = None
        leaderboard_span_id = request.POST.get('spanID')
        delete = request.POST.get('delete')
        name = escape(request.POST.get('name', ''))
        start = request.POST.get('start')
        end = request.POST.get('end')
        # Convert dates if they exist
        if start and end:
            start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()
        # If we're deleting the span
        if delete:
            action = "Leaderboard Span Deleted Successfully!"
            leaderboard_span = leaderboards_service.leaderboard_span_or_404(delete)
            # Delete the leaderboard span
            leaderboard_span.delete()
        # If we're editing the leaderboard span
        elif leaderboard_span_id and name and start and end:
            action = "Leaderboard Span Edited Successfully!"
            leaderboard_span = leaderboards_service.leaderboard_span_or_404(leaderboard_span_id)
            leaderboard_span.name = name
            leaderboard_span.start_date = start_date
            leaderboard_span.end_date = end_date
        # If we're creating the player
        elif name and start and end:
            action = "Leaderboard Span Created Successfully!"
            leaderboard_span = leaderboards_service.create_leaderboard_span(
                                                                  name,
                                                                  context['channel'],
                                                                  start_date,
                                                                  end_date)
        else:
            error = 'Leaderboard Span Name, Start Date, and End Date required!'
        # If there were no errors, save the leaderboard span
        if not error and not delete:
            leaderboard_span.save()

        context.update(
            {'action': action,
             'error': error})
        return render(request,
                      self.template_name,
                      context)


class ChannelAdminsView(view_utils.ShowView):
    template_name = 'channels/channel_admins.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        channel_admins = channels_service.get_channel_admins(context['channel'].id)
        context.update(
            {'channel_admins': channel_admins})
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        action = None
        error = None
        add = request.POST.get('add')
        edit = request.POST.get('edit')
        context = self.get_default_channel_context(request, *args, **kwargs)
        # If we're adding a new admin
        if add:
            username = request.POST.get('username')
            # Get the user profile
            user_profile = users_service.fetch_user_profile(username=username)
            # Add the channel admin by username
            added = channels_service.add_channel_admin(context['channel'], user_profile.user)
            # If the admin was added
            if added:
                action = "Added Channel Admin Successfully!"
            # The user was already an admin
            else:
                error = "Failed to add new admin!"
        # If we're editing existing admins
        elif edit:
            # Get the channel admins
            channel_admins = channels_service.get_channel_admins(context['channel'].id)
            # Make sure they didn't remove all the owners
            if not 'owner' in [request.POST.get(str(admin.id)) for admin in channel_admins]:
                error = "You must have at least one Channel Owner!"
            else:
                # Loop through the existing admins
                for admin in channel_admins:
                    # Determine what action to take from the post
                    admin_action = request.POST.get(str(admin.id))
                    # If we are making them an owner
                    if admin_action == 'owner':
                        channels_service.add_channel_owner(context['channel'], admin.user)
                    # If we are making them an admin
                    elif admin_action == 'admin':
                        # Remove them as an owner (the only possible choice here)
                        channels_service.remove_channel_owner(context['channel'], admin.user)
                    # If we are removing them as an admin
                    elif admin_action == 'remove':
                        # Remove them as an owner
                        channels_service.remove_channel_owner(context['channel'], admin.user)
                        # Remove them as an admin
                        channels_service.remove_channel_admin(context['channel'], admin.user)
                action = "Admins Updated Successfully!"

        # Get updated channel admins
        channel_admins = channels_service.get_channel_admins(context['channel'].id)
        context.update(
            {'channel_admins': channel_admins,
             'action': action,
             'error': error})
        return render(request,
                      self.template_name,
                      context)


class ChannelExportEmailsView(view_utils.ShowView):
    template_name = 'channels/channel_export_emails.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        # Add the Channel's shows to the context
        context.update({
            'shows': shows_service.fetch_shows_by_channel(context['channel'].id)
        })
        return render(request,
                      self.template_name,
                      context)

    def post(self, request, *args, **kwargs):
        show_id = request.POST.get('show')
        context = self.get_default_channel_context(request, *args, **kwargs)
        # If something was selected
        if show_id:
            filehandle = StringIO.StringIO()
            fieldnames = [
                'email',
                'user_id',
                'username',
                'first_name',
                'last_name',
                'suggestion_wins',
                'points']
            # If the user wants to export all e-mails
            if show_id == 'all':
                # Set the name of the response file
                export_filename = '{0}_emails'.format(context['channel'].name)
                # Fetch all the channel users
                channel_users = channels_service.fetch_channel_users(context['channel'],
                                                                     leaderboard_sort=True)
                # Add the extra fields for export
                fieldnames += [
                    'show_wins',
                    'channel_rank']
                # Create the csv writer
                writer = csv.DictWriter(filehandle,
                                        fieldnames=fieldnames,
                                        delimiter=',',
                                        quotechar='"',
                                        quoting=csv.QUOTE_NONNUMERIC)
                # Write the header row
                writer.writeheader()
                rank = 1
                for channel_user in channel_users:
                    # Get the user from the channel user
                    user = channel_user.user
                    # Create the csv output row
                    row = {'email': user.email,
                           'user_id': user.id,
                           'username': user.username,
                           'first_name': user.first_name,
                           'last_name': user.last_name,
                           'suggestion_wins': channel_user.suggestion_wins,
                           'points': channel_user.points,
                           'show_wins': channel_user.show_wins,
                           'channel_rank': rank}
                    # Write the row to the filehandle
                    writer.writerow(row)
                    # Increase the rank
                    rank += 1
            # If the user wants to export e-mails for a particular show
            else:
                # Get the selected show
                show = shows_service.show_or_404(show_id)
                # Set the name of the response file to the show's created date
                export_filename = '{0}-{1}-{2}_show_emails'.format(show.created.year,
                                                                   show.created.month,
                                                                   show.created.day)
                # Add the extra fields for export
                fieldnames += ['show_rank']
                # Create the csv writer
                writer = csv.DictWriter(filehandle,
                                        fieldnames=fieldnames,
                                        delimiter=',',
                                        quotechar='"',
                                        quoting=csv.QUOTE_NONNUMERIC)
                # Write the header row
                writer.writeheader()
                # Get the leaderboard entry for the show,
                # excluding entries without users attached
                leaderboard_entries = leaderboards_service.fetch_leaderboard_entries_by_show(
                                                show.id,
                                                leaderboard_order=True)
                rank = 1
                for leaderboard_entry in leaderboard_entries:
                    # Get the user from the leaderboard entry
                    user = leaderboard_entry.user
                    # Create the csv output row
                    row = {'email': user.email,
                           'user_id': user.id,
                           'username': user.username,
                           'first_name': user.first_name,
                           'last_name': user.last_name,
                           'suggestion_wins': leaderboard_entry.wins,
                           'points': leaderboard_entry.points,
                           'show_rank': rank}
                    # Write the row to the filehandle
                    writer.writerow(row)
                    # Increase the rank
                    rank += 1
            # Reset the filehandle to the beginning
            filehandle.seek(0)
            # Return the response as a csv file
            response = HttpResponse(filehandle.read(),
                                    content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment;filename={0}.csv'.format(export_filename)
            return response
        else:
            # Add the Channel's shows to the context
            context.update({
                'shows': shows_service.fetch_shows_by_channel(context['channel'].id)
            })
            return render(request,
                          self.template_name,
                          context)