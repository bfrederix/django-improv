import datetime
import re
import pytz
import cloudinary.uploader

from django.shortcuts import render, redirect
from django.utils.html import escape, strip_tags
from django.core.exceptions import ObjectDoesNotExist

from channels.models import (Channel, ChannelAddress, ChannelOwner,
                             ChannelAdmin, SuggestionPool, VoteType)
from channels import service as channels_service
from players import service as players_service
from shows import service as shows_service
from users import service as users_service
from utilities import views as view_utils


def name_validator(name):
    # If it's an invalid name
    if not re.match('[0-9a-z-]', name):
        return "Invalid Channel Name"
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

        error = name_validator(request.POST.get('name'))
        next_show = request.POST.get('next_show')
        channel_update = {"name": request.POST.get('name'),
                          "display_name": request.POST.get('display_name'),
                          "short_description": strip_tags(request.POST.get('short_description', '')),
                          "description": strip_tags(request.POST.get('description', '')),
                          "website": strip_tags(request.POST.get('website', '')),
                          "facebook_page": strip_tags(request.POST.get('facebook_page', '')),
                          "buy_tickets_link": strip_tags(request.POST.get('buy_tickets_link', '')),
                          "next_show": next_show or None,
                          "navbar_color": request.POST.get('navbar_color'),
                          "background_color": request.POST.get('background_color')}
        address_update = {"street": request.POST.get('street'),
                          "city": request.POST.get('city'),
                          "state": request.POST.get('state'),
                          "zipcode": request.POST.get('zipcode')}
        image_update = {"team_photo_url": request.FILES.get('teamPhotoFile')}
        # If this channel doesn't already exist (and there's no errors)
        if not context['channel'] and not error:
            context['channel'] = Channel(**channel_update)
        # Otherwise the channel exists (and there's no errors)
        elif not error:
            for field, value in channel_update.items():
                setattr(context['channel'], field, value)
        context['channel'].save()
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
        if uploaded_file and not error:
            cloud_response = cloudinary.uploader.upload(uploaded_file,
                                                        folder="players",
                                                        public_id=player.id,
                                                        invalidate=True)
            player.photo_url = cloud_response.get('secure_url')
        # If there were no errors, save the player
        if not error:
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

        if not error:
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

        if not error:
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
