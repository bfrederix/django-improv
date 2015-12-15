from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape

import cloudinary.uploader

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


class ChannelPlayersView(View):
    template_name = 'channels/channel_players.html'

    def get(self, request, *args, **kwargs):
        channel_name = kwargs.get('channel_name')
        channel = channels_service.channel_or_404(channel_name)
        is_channel_admin = channels_service.check_is_channel_admin(channel,
                                                                   getattr(request.user, 'id'))
        return render(request,
                      self.template_name,
                      {'channel': channel,
                       'is_channel_admin': is_channel_admin})

    def post(self, request, *args, **kwargs):
        channel_name = kwargs.get('channel_name')
        channel = channels_service.channel_or_404(channel_name)
        is_channel_admin = channels_service.check_is_channel_admin(channel,
                                                                   getattr(request.user, 'id'))
        if is_channel_admin:
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
            # This will fail if file size is > 2097152:
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
                       'is_channel_admin': is_channel_admin,
                       'action': action,
                       'error': error})