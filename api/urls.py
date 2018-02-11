from django.urls import path
from django.conf.urls import include
from . import views

urlpatterns = [
    path(r'', views.api_root, name='api_root'),
    path(r'tags/', views.TagList.as_view(), name='tag_list'),
    path(r'tags/<str:pk>/', views.TagDetails.as_view(), name='tag_detail'),
    path(r'bookmarks/', views.BookmarkList.as_view(), name='bookmark_list'),
    path(r'bookmarks/<int:pk>/', views.BookmarkDetails.as_view(), name='bookmark_detail'),
    path(r'users/', views.UserList.as_view(), name='user_list'),
    path(r'users/<int:pk>/', views.UserDetails.as_view(), name='user_detail'),
    path(r'users/<int:pk>/token/', views.UserToken.as_view(), name='user_token'),
    path(r"auth/", include('rest_framework.urls'))
]
