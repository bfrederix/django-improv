from django.conf.urls import url

from leaderboards import views

urlpatterns = [
    url(r'^$', views.ChannelLeaderboardsView.as_view(), name="channel_leaderboards"),
    url(r'^show/(?P<show_id>[0-9]+)/$', views.ChannelShowLeaderboardView.as_view(), name="channel_show_leaderboard"),
]