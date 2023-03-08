from django.urls import path, include
from rest_framework import routers

from api.views import (
    UserViewSet,
    TokenViewSet,
    SignUpViewSet,
    TitleViewSet,
    GenreViewSet,
    CategoryViewSet,
    ReviewViewSet,
    CommentViewSet
)


app_name = 'api'

routes_v1 = routers.DefaultRouter()
routes_v1.register('categories', CategoryViewSet, basename='categories')
routes_v1.register('titles', TitleViewSet, basename='titles')
routes_v1.register('genres', GenreViewSet, basename='genres')
routes_v1.register('users', UserViewSet)
routes_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews'
)
routes_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments'
)

path_auth_v1 = [
    path('signup/', SignUpViewSet.as_view(), name='signup'),
    path('token/', TokenViewSet.as_view(), name='token'),
]

urlpatterns = [
    path('v1/', include(routes_v1.urls)),
    path('v1/auth/', include(path_auth_v1))
]
