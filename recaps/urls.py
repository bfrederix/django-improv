from django.conf.urls import url

from recaps import views

urlpatterns = [
    url(r'^$', views.ChannelRecapsView.as_view(), name="channel_recaps"),
]