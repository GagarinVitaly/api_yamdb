from django.urls import include, path
from rest_framework import routers

from api.views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SignUpViewSet,
    TitleViewSet,
    TokenViewSet,
    UserViewSet,)


router1 = routers.DefaultRouter()
router1.register('users', UserViewSet, basename='users')
router1.register('categories', CategoryViewSet, basename='categories')
router1.register('genres', GenreViewSet, basename='genres')
router1.register('titles', TitleViewSet, basename='titles')
router1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews')
router1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments')

urlpatterns = [
    path('v1/', include(router1.urls)),
    path(
        'v1/auth/signup/',
        SignUpViewSet.as_view({'post': 'create'}),
        name='signup'),
    path(
        'v1/auth/token/',
        TokenViewSet.as_view({'post': 'create'}),
        name='token'),
]
