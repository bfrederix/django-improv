from django.conf.urls import url

from leaderboards import views

urlpatterns = [
    url(r'^$', views.ChannelLeaderboardsView.as_view(), name="channel_leaderboards"),
    url(r'^show/(?P<show_id>[0-9]+)/$', views.ChannelLeaderboardsView.as_view(), name="channel_show_leaderboards"),
    url(r'^(?P<start>\d{8})/(?P<end>\d{8})/$', views.ChannelLeaderboardSpansView.as_view(), name="channel_leaderboard_spans"),
]