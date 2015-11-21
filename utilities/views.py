from django.http import HttpResponse


def robots_txt(request):
    robots_txt = """User-agent: *
Disallow: /"""

    live_txt = """User-agent: *
Allow: /$
Allow: /leaderboards
Allow: /recap
Allow: /user
Allow: /medals
Disallow: /"""
    return HttpResponse(robots_txt, content_type='text/plain')

def loader_io(request):
    robots_txt = "loaderio-9b6fa50492da1609dc61b9198b767688"
    return HttpResponse(robots_txt, content_type='text/plain')