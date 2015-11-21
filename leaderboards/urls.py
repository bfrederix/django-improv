from django.conf.urls import url

from leaderboards import views

urlpatterns = [
    url(r'^$', views.ChannelLeaderboardsView.as_view(), name="channel_leaderboards"),
]