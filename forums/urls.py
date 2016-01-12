from django.conf.urls import url

from forums import views

urlpatterns = [
    # All Forums
    url(r'^$', views.ForumHomeView.as_view(), name="forums_home"),
    # Forum Threads
    url(r'^(?P<forum_name>[a-zA-Z0-9-]+)/$', views.ForumThreadListView.as_view(), name="forums_thread_list"),
    # Forum Create Thread
    url(r'^(?P<forum_name>[a-zA-Z0-9-]+)/new/$', views.ForumCreateThreadView.as_view(), name="forums_create_thread"),
    # Forum Thread
    url(r'^(?P<forum_name>[a-zA-Z0-9-]+)/(?P<thread_id>[0-9]+)/$', views.ForumThreadView.as_view(), name="forums_thread"),
]