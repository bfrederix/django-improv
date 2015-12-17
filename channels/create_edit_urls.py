from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from channels import views
from utilities.decorators import channel_admin_required

urlpatterns = [
    url(r'^$', login_required(views.ChannelCreateEditView.as_view()), name="channel_create"),
    url(r'^(?P<channel_id>[0-9]+)/$', channel_admin_required(views.ChannelCreateEditView.as_view()), name="channel_edit"),
]