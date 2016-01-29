import datetime
import pytz

from django.views.generic import View
from django.utils.html import strip_tags
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from forums.models import Forum, Thread, Reply
from channels import service as channels_service
from users import service as users_service


def get_paginated(request, objects, per_page=25):
    paginator = Paginator(objects, per_page) # How many per page

    page = request.GET.get('page')
    try:
        paginated = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated = paginator.page(paginator.num_pages)
    return paginated


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

    def paginated_threads(self, request, forum):
        thread_list = Thread.objects.filter(forum=forum).order_by('-sticky','-updated')
        return get_paginated(request, thread_list)

    def get(self, request, *args, **kwargs):
        forum_name = kwargs.get('forum_name')
        forum = get_object_or_404(Forum, name=forum_name)
        threads = self.paginated_threads(request, forum)
        admin_channels = channels_service.get_channels_by_admin(getattr(request.user, 'id'))
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))
        return render(request,
                      self.template_name,
                      {'forum': forum,
                       'threads': threads,
                       'user_profile': user_profile,
                       'admin_channels': admin_channels,
                       'page': int(request.GET.get('page', 1))})

    def post(self, request, *args, **kwargs):
        forum_name = kwargs.get('forum_name')
        forum = get_object_or_404(Forum, name=forum_name)
        admin_channels = channels_service.get_channels_by_admin(getattr(request.user, 'id'))
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))
        delete_thread = request.POST.get('delete_thread')
        # Super user delete thread
        if request.user.is_superuser and delete_thread:
            # Delete all the replies
            for reply in Reply.objects.filter(thread=delete_thread):
                reply.delete()
            # Delete the thread
            Thread.objects.get(id=delete_thread).delete()
        threads = self.paginated_threads(request, forum)

        return render(request,
                      self.template_name,
                      {'forum': forum,
                       'threads': threads,
                       'user_profile': user_profile,
                       'admin_channels': admin_channels,
                       'page': int(request.GET.get('page', 1))})


class ForumCreateThreadView(View):
    template_name = 'forums/forum_create_thread.html'

    def get(self, request, *args, **kwargs):
        error = False
        forum_name = kwargs.get('forum_name')
        forum = get_object_or_404(Forum, name=forum_name)
        admin_channels = channels_service.get_channels_by_admin(getattr(request.user, 'id'))
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))
        return render(request,
                      self.template_name,
                      {'forum': forum,
                       'user_profile': user_profile,
                       'admin_channels': admin_channels})

    def post(self, request, *args, **kwargs):
        error = False
        forum_name = kwargs.get('forum_name')
        forum = get_object_or_404(Forum, name=forum_name)
        admin_channels = channels_service.get_channels_by_admin(getattr(request.user, 'id'))
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        # Forum user posting a new thread
        if subject and message:
            creation_datetime = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            Thread.objects.get_or_create(
                  forum=forum,
                  subject=subject,
                  message=message,
                  sticky=False,
                  creator=request.user,
                  created=creation_datetime,
                  updated=creation_datetime)
        else:
            error = "Subject and message must not be empty"

        if error:
            return render(request,
                          self.template_name,
                          {'error': error,
                           'forum': forum,
                           'user_profile': user_profile,
                           'admin_channels': admin_channels,
                           'page': int(request.GET.get('page', 1))})
        else:
            return redirect('forums_thread_list', forum_name=forum.name)


class ForumThreadView(View):
    template_name = 'forums/forum_thread.html'

    def paginated_replies(self, request, thread):
        reply_list = Reply.objects.filter(thread=thread)
        return get_paginated(request, reply_list)

    def get(self, request, *args, **kwargs):
        forum_name = kwargs.get('forum_name')
        thread_id = kwargs.get('thread_id')
        forum = get_object_or_404(Forum, name=forum_name)
        thread = get_object_or_404(Thread, id=thread_id)
        replies = self.paginated_replies(request, thread)
        admin_channels = channels_service.get_channels_by_admin(getattr(request.user, 'id'))
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))
        return render(request,
                      self.template_name,
                      {'forum': forum,
                       'thread': thread,
                       'replies': replies,
                       'user_profile': user_profile,
                       'admin_channels': admin_channels,
                       'page': int(request.GET.get('page', 1))})

    def post(self, request, *args, **kwargs):
        error = False
        forum_name = kwargs.get('forum_name')
        thread_id = kwargs.get('thread_id')
        forum = get_object_or_404(Forum, name=forum_name)
        thread = get_object_or_404(Thread, id=thread_id)
        admin_channels = channels_service.get_channels_by_admin(getattr(request.user, 'id'))
        user_profile = users_service.fetch_user_profile(getattr(request.user, 'id'))
        message = strip_tags(request.POST.get('message', ''))
        delete_reply = request.POST.get('delete_reply')
        # Superuser deleting a thread reply
        if request.user.is_superuser and delete_reply:
            Reply.objects.get(id=delete_reply).delete()
        # Forum user posting a reply
        elif message:
            Reply.objects.get_or_create(
                  forum=forum,
                  thread=thread,
                  message=message,
                  creator=request.user,
                  created=datetime.datetime.utcnow().replace(tzinfo=pytz.utc))
        else:
            error = "Message must not be empty"
        replies = self.paginated_replies(request, thread)

        return render(request,
                      self.template_name,
                      {'error': error,
                       'forum': forum,
                       'thread': thread,
                       'replies': replies,
                       'user_profile': user_profile,
                       'admin_channels': admin_channels,
                       'page': int(request.GET.get('page', 1))})