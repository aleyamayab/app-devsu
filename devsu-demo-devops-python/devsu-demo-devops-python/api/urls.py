from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, health

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', health),
]
