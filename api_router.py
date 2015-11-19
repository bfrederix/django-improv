from rest_framework import routers
#from players import api_views as players_api_views
from users import api_views as users_api_views

router = routers.DefaultRouter()
#router.register(r'players', players_api_views.PlayerViewSet)
router.register(r'users', users_api_views.UserProfileViewSet)

