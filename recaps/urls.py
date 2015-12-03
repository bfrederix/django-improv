from django.conf.urls import url

from recaps import views

urlpatterns = [
    url(r'^$', views.ChannelRecapsView.as_view(), name="channel_recaps"),
    url(r'^show/(?P<show_id>[0-9]+)/$', views.ChannelRecapsView.as_view(), name="channel_show_recaps"),
]