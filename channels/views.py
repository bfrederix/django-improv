from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape

import cloudinary.uploader

from channels.models import (Channel, ChannelAddress, ChannelOwner,
                             ChannelAdmin)
from channels import service as channels_service
from users import service as users_service
from players import service as players_service


class ChannelHomeView(View):
    template_name = 'channels/channel_home.html'

    def get(self, request, *args, **kwargs):
        channel_name = kwargs.get('channel_name')
        channel = channels_service.channel_or_404(channel_name)
        is_channel_admin = channels_service.check_is_channel_admin(channel,
                                                                   getattr(request.user, 'id'))
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))
        return render(request,
                      self.template_name,
                      {'channel': channel,
                       'user_profile': user_profile,
                       'is_channel_admin': is_channel_admin})

@csrf_exempt
def channel_user_update(request, *args, **kwargs):
    channel_name = kwargs.get('channel_name')
    user_id = kwargs.get('user_id')
    channel = channels_service.channel_or_404(channel_name)
    if request.method == 'POST' and user_id:
        channels_service.update_channel_user(channel.id, user_id)
        return HttpResponse("Channel User Updated", content_type='text/plain')
    return HttpResponse("Not Updated", content_type='text/plain')


class ChannelCreateEditView(View):
    template_name = 'channels/channel_create_edit.html'

    def get(self, request, *args, **kwargs):
        channel_id = kwargs.get('channel_id')
        if channel_id:
            channel = channels_service.channel_or_404(channel_id, channel_id=True)
        else:
            channel = None
        return render(request,
                      self.template_name,
                      {'channel': channel})

    def post(self, request, *args, **kwargs):
        action = None
        channel_id = kwargs.get('channel_id')
        if channel_id:
            channel = channels_service.channel_or_404(channel_id, channel_id=True)
            action = "Channel Edited Successfully!"
        else:
            channel = None

        error = None
        next_show = request.POST.get('next_show')
        channel_update = {"name": request.POST.get('name'),
                          "display_name": request.POST.get('display_name'),
                          "short_description": request.POST.get('short_description'),
                          "description": request.POST.get('description'),
                          "website": request.POST.get('website'),
                          "facebook_page": request.POST.get('facebook_page'),
                          "buy_tickets_link": request.POST.get('buy_tickets_link'),
                          "next_show": next_show or None,
                          "timezone": request.POST.get('timezone')}
        address_update = {"street": request.POST.get('street'),
                          "city": request.POST.get('city'),
                          "state": request.POST.get('state'),
                          "zipcode": request.POST.get('zipcode')}
        image_update = {"logo_url": request.FILES.get('logoFile'),
                        "team_photo_url": request.FILES.get('teamPhotoFile')}
        if not channel:
            channel = Channel(**channel_update)
        else:
            for field, value in channel_update.items():
                setattr(channel, field, value)
        channel.save()
        # Update or create images in cloudinary
        for field_name, img_file in image_update.items():
            if img_file and not error:
                public_id = "{0}_{1}".format(field_name, channel.id)
                cloud_response = cloudinary.uploader.upload(img_file,
                                                            folder="channels",
                                                            public_id=public_id,
                                                            invalidate=True)
                setattr(channel, field_name, cloud_response.get('secure_url'))
        # If there were no errors, save the channel
        if not error:
            # Create/Update the channel address
            if not channel.address:
                channel_address = ChannelAddress(**address_update)
                channel_address.save()
                channel.address = channel_address
            else:
                for field, value in address_update.items():
                    setattr(channel.address, field, value)
                channel.address.save()
            channel.save()
            # If this is a new channel
            if not channel_id:
                # Make the current user the owner and admin of the channel
                ChannelOwner.objects.get_or_create(channel=channel,
                                                   user=request.user)
                ChannelAdmin.objects.get_or_create(channel=channel,
                                                   user=request.user)
                # redirect to the newly created channel
                return redirect('channel_home', channel_name=channel.name)

        return render(request,
                      self.template_name,
                      {'channel': channel,
                       'action': action,
                       'error': error})


class ChannelPlayersView(View):
    template_name = 'channels/channel_players.html'

    def get(self, request, *args, **kwargs):
        channel_name = kwargs.get('channel_name')
        channel = channels_service.channel_or_404(channel_name)
        return render(request,
                      self.template_name,
                      {'channel': channel})

    def post(self, request, *args, **kwargs):
        channel_name = kwargs.get('channel_name')
        channel = channels_service.channel_or_404(channel_name)
        error = None
        action = None
        player_id = request.POST.get('playerID')
        player_name = escape(request.POST.get('player_name', ''))
        active = bool(request.POST.get('active', False))
        star = bool(request.POST.get('star', False))
        if player_id and player_name:
            action = "Player Edited Successfully!"
            player = players_service.player_or_404(player_id)
            player.name = player_name
            player.active = active
            player.star = star
        elif player_name:
            action = "Player Created Successfully!"
            player = players_service.create_player(player_name,
                                                   channel,
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


        return render(request,
                      self.template_name,
                      {'channel': channel,
                       'action': action,
                       'error': error})