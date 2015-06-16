from django.http import HttpResponse


def robots_txt(request):
    robots_txt = """User-agent: *
Allow: /$
Allow: /leaderboards
Allow: /recap
Allow: /user
Allow: /medals
Disallow: /"""
    return HttpResponse(robots_txt, content_type='text/plain')