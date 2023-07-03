from django.urls import include, path
from rest_framework import routers

from api.views import SignUpViewSet, TokenViewSet, UserViewSet

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path('v1/', include(router.urls)),
    path(
        'v1/auth/signup/',
        SignUpViewSet.as_view({'post': 'create'}),
        name='signup'),
    path(
        'v1/auth/token/',
        TokenViewSet.as_view({'post': 'create'}),
        name='token'),
]
