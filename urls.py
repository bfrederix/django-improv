"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps import views

from utilities import views as view_utils
from api_router import router
from sitemaps import sitemaps

urlpatterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + [
    url(r'^api/v1/', include(router.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^robots\.txt$', view_utils.robots_txt, name="robots"),
    url(r'^08D99316C0F20BD27FF8A5F2F452AB52\.txt$', view_utils.ssl_verify),
    url(r'^loaderio-9b6fa50492da1609dc61b9198b767688.txt$', view_utils.loader_io, name="loader_io"),
    url(r'^auth/logout/$', 'django.contrib.auth.views.logout', name='auth_logout'),
    url(r'^auth/', include('rest_framework_social_oauth2.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^forums/', include('forums.urls')),
    url(r'^$', include('home.urls')),
    url(r'^sitemap\.xml$', views.index, {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', views.sitemap, {'sitemaps': sitemaps}),
    url(r'^channel/browse/', include('channels.browse_urls')),
    url(r'^channel/premium/', include('channels.payment_urls')),
    url(r'^channel/', include('channels.create_edit_urls')),
    url(r'^(?P<channel_name>[a-zA-Z0-9-]+)/show/', include('shows.urls')),
    url(r'^(?P<channel_name>[a-zA-Z0-9-]+)/leaderboards/', include('leaderboards.urls')),
    url(r'^(?P<channel_name>[a-zA-Z0-9-]+)/medals/', include('leaderboards.medal_urls')),
    url(r'^(?P<channel_name>[a-zA-Z0-9-]+)/recaps/', include('recaps.urls')),
    url(r'^(?P<channel_name>[a-zA-Z0-9-]+)/', include('channels.urls')),
]
