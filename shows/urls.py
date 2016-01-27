from django.conf.urls import url

from shows import views
from utilities.decorators import channel_admin_required

urlpatterns = [
    url(r'^(?P<show_id>[0-9]+)/controller/$', channel_admin_required(views.ShowControllerView.as_view()), name="show_controller"),
    url(r'^(?P<show_id>[0-9]+)/display/$', channel_admin_required(views.ShowDisplayView.as_view()), name="show_display"),
    url(r'^(?P<show_id>[0-9]+)/live_vote/$', views.ShowLiveVoteView.as_view(), name="show_live_vote"),
    url(r'^(?P<show_id>[0-9]+)/suggestion_pool/(?P<suggestion_pool_id>[0-9]+)/$', views.ShowSuggestionPoolView.as_view(), name="show_suggestion_pool"),
]