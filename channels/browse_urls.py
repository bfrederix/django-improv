from django.conf.urls import url

from channels import views


urlpatterns = [
    # All users
    url(r'^$', views.ChannelBrowseView.as_view(), name="channel_browse"),
]