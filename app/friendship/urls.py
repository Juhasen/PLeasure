from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register('friends', views.UserFriendsViewSet)


app_name = 'friendship'

urlpatterns = [
    path('', include(router.urls)),
]
