from django.conf.urls import url

from channels import views
from utilities.decorators import channel_admin_required, channel_owner_required

urlpatterns = [
    # All users
    url(r'^$', views.ChannelHomeView.as_view(), name="channel_home"),
    #url(r'^about/$', views.ChannelAboutView.as_view(), name="channel_about"),
    # Admin only
    url(r'^players/$', channel_admin_required(views.ChannelPlayersView.as_view()), name="channel_players"),
    url(r'^suggestion_pools/$', channel_admin_required(views.ChannelSuggestionPoolsView.as_view()), name="channel_suggestion_pools"),
    url(r'^vote_types/$', channel_admin_required(views.ChannelVoteTypesView.as_view()), name="channel_vote_types"),
    url(r'^shows/$', channel_admin_required(views.ChannelShowsView.as_view()), name="channel_shows"),
    url(r'^pre_show_instructions/$', channel_admin_required(views.ChannelPreShowView.as_view()), name="channel_pre_show"),
    url(r'^admins/$', channel_owner_required(views.ChannelAdminsView.as_view()), name="channel_admins"),
]