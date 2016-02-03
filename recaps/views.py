from django.shortcuts import render
from django.views.generic import View

from channels.service import channel_or_404, check_is_channel_admin
from shows.service import show_or_404
from utilities import views as view_utils


class ChannelRecapsView(view_utils.ShowView):
    template_name = 'recaps/channel_recaps.html'

    def get(self, request, *args, **kwargs):
        context = self.get_default_channel_context(request, *args, **kwargs)
        show_id = kwargs.get('show_id')
        if show_id:
            show = show_or_404(show_id)
        else:
            show = None

        context.update({'show': show})

        return render(request,
                      self.template_name,
                      context)