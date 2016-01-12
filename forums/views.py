import datetime
import pytz

from django.views.generic import View
from django.shortcuts import render, get_object_or_404

from forums.models import Forum, Thread, Reply
from channels import service as channels_service
from users import service as users_service


class ForumHomeView(View):
    template_name = 'forums/forum_home.html'

    def get(self, request, *args, **kwargs):
        forums = Forum.objects.all()
        admin_channels = channels_service.get_channels_by_admin(getattr(request.user, 'id'))
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))
        return render(request,
                      self.template_name,
                      {'forums': forums,
                       'user_profile': user_profile,
                       'admin_channels': admin_channels})


class ForumThreadListView(View):
    template_name = 'forums/forum_thread_list.html'

    def get(self, request, *args, **kwargs):
        forum_name = kwargs.get('forum_name')
        forum = get_object_or_404(Forum, name=forum_name)
        threads = Thread.objects.filter(forum=forum).order_by('-sticky','-updated')
        admin_channels = channels_service.get_channels_by_admin(getattr(request.user, 'id'))
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))
        return render(request,
                      self.template_name,
                      {'forum': forum,
                       'threads': threads,
                       'user_profile': user_profile,
                       'admin_channels': admin_channels})


class ForumCreateThreadView(View):
    template_name = 'forums/forum_thread_list.html'

    def get(self, request, *args, **kwargs):
        forums = Forum.objects.all()
        admin_channels = channels_service.get_channels_by_admin(getattr(request.user, 'id'))
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))
        return render(request,
                      self.template_name,
                      {'forums': forums,
                       'user_profile': user_profile,
                       'admin_channels': admin_channels})


class ForumThreadView(View):
    template_name = 'forums/forum_thread.html'

    def get(self, request, *args, **kwargs):
        forum_name = kwargs.get('forum_name')
        thread_id = kwargs.get('thread_id')
        forum = get_object_or_404(Forum, name=forum_name)
        thread = get_object_or_404(Thread, id=thread_id)
        replies = Reply.objects.filter(thread=thread)
        admin_channels = channels_service.get_channels_by_admin(getattr(request.user, 'id'))
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))
        return render(request,
                      self.template_name,
                      {'forum': forum,
                       'thread': thread,
                       'replies': replies,
                       'user_profile': user_profile,
                       'admin_channels': admin_channels})

    def post(self, request, *args, **kwargs):
        error = False
        forum_name = kwargs.get('forum_name')
        thread_id = kwargs.get('thread_id')
        forum = get_object_or_404(Forum, name=forum_name)
        thread = get_object_or_404(Thread, id=thread_id)
        replies = Reply.objects.filter(thread=thread)
        admin_channels = channels_service.get_channels_by_admin(getattr(request.user, 'id'))
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))
        message = request.POST.get('message', '')
        if message:
            Reply.objects.get_or_create(
                  forum=forum,
                  thread=thread,
                  message=message,
                  creator=request.user,
                  created=datetime.datetime.utcnow().replace(tzinfo=pytz.utc))
        else:
            error = "Message must not be empty"

        return render(request,
                      self.template_name,
                      {'error': error,
                       'forum': forum,
                       'thread': thread,
                       'replies': replies,
                       'user_profile': user_profile,
                       'admin_channels': admin_channels})