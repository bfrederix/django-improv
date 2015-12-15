from django.conf.urls import url

from channels import views

urlpatterns = [
    url(r'^$', views.ChannelHomeView.as_view(), name="channel_home"),
    url(r'^user_update/(?P<user_id>[0-9]+)/$', views.channel_user_update, name="channel_user_update"),
    url(r'^players/$', views.ChannelPlayersView.as_view(), name="channel_players"),
]