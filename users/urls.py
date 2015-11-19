from django.conf.urls import url

from users import views

urlpatterns = [
    url(r'^opt_in_preferences/(?P<backend>\w+)/$', views.OptInPreferencesView.as_view(), name="opt_in_preferences"),
]