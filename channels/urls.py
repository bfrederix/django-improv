from django.conf.urls import url

from channels import views
from utilities.decorators import channel_admin_required

urlpatterns = [
    url(r'^$', views.ChannelHomeView.as_view(), name="channel_home"),
    url(r'^user_update/(?P<user_id>[0-9]+)/$', views.channel_user_update, name="channel_user_update"),
    url(r'^players/$', channel_admin_required(views.ChannelPlayersView.as_view()), name="channel_players"),
    url(r'^suggestion_pools/$', channel_admin_required(views.ChannelSuggestionPoolsView.as_view()), name="channel_suggestion_pools"),
]