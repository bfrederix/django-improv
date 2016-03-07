from django.conf.urls import url

from leaderboards import views

urlpatterns = [
    url(r'^$', views.ChannelMedalsView.as_view(), name="channel_medals"),
]