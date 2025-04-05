from rest_framework.routers import DefaultRouter
from accounts.views import UserViewSet
from django.urls import path, include


router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]