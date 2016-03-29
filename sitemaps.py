from django.contrib.sitemaps import Sitemap
from django.core.urlresolvers import reverse

from channels.models import Channel
from users.models import User


class ChannelSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return Channel.objects.filter(archived=False)

    def location(self, obj):
        return reverse('channel_home', kwargs={'channel_name': obj.name})


class UsersSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.4

    def __init__(self, *args, **kwargs):
        self.start = kwargs.get('start')
        self.end = kwargs.get('end')
        super(UsersSitemap, self).__init__()

    def items(self):
        return User.objects.all().order_by('id')[self.start:self.end]

    def location(self, obj):
        return reverse('user_account', kwargs={'user_id': obj.id})


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.5

    def items(self):
        return ['dumpedit_home', 'forums_home']

    def location(self, item):
        return reverse(item)


def get_sitemaps():
    sitemaps = {'channels': ChannelSitemap,
                'static': StaticViewSitemap}
    # Get the count of all the users
    user_count = User.objects.all().count()
    prev_end = 0
    count = 0
    # Make a loop starting with 0-50,000
    # Running up until the user count
    # Stepping through by 50,000
    for i in range(50000, user_count, 50000):
        count += 1
        user_key = "user-{0}".format(count)
        # Generate another user sitemap section
        sitemaps[user_key] = UsersSitemap(start=prev_end, end=i)
        prev_end = i
    # If there is a leftover section
    if prev_end < user_count:
        count += 1
        user_key = "user-{0}".format(count)
        # Generate the leftover user sitemap section
        sitemaps[user_key] = UsersSitemap(start=prev_end, end=user_count)
    return sitemaps

sitemaps = get_sitemaps()