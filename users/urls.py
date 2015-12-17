from django.conf.urls import url

from users import views

urlpatterns = [
    url(r'^login/$', views.UserLoginView.as_view(), name="user_login"),
    url(r'^opt_in_preferences/(?P<backend>\w+)/$', views.OptInPreferencesView.as_view(), name="opt_in_preferences"),
    url(r'^(?P<user_id>[0-9]+)/$', views.UserAccountView.as_view(), name="user_account"),
]