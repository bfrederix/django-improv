from django.conf.urls import include, url, patterns
from utilities.decorators import channel_admin_required, decorate_include

urlpatterns = []

# Adding stripe to the channel with channel admin required
urlpatterns += patterns(
    '',
    url('^payments/', decorate_include(channel_admin_required, include('djstripe.urls', namespace="djstripe"))),
)