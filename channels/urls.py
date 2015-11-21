from django.conf.urls import url

from channels import views

urlpatterns = [
    url(r'^(?P<channel_name>[a-zA-Z0-9-]+)/$', views.ChannelHomeView.as_view(), name="channel_home"),
    url(r'^(?P<channel_name>[a-zA-Z0-9-]+)/leaderboards/$', views.ChannelLeaderboardsView.as_view(), name="channel_leaderboards"),
    #url(r'^(?P<channel_name>[a-zA-Z0-9-]+)/leaderboards/(?P<show>\d+)/$', views.ChannelLeaderboardsView.as_view()),
    #url(r'^(?P<channel_name>[a-zA-Z0-9-]+)/leaderboards/(\d{8})/(\d{8})/$', views.ChannelLeaderboardsView.as_view()),
]