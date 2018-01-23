from .models import Tag, Bookmark
from rest_framework import generics
from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import permissions
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token

from .serializers import TagSerializer, BookmarkSerializer, UserSerializer, TokenSerializer
from .permissions import IsOwnerOrReadonly, IsOwner

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user_list', request=request, format=format),
        'tags': reverse('tag_list', request=request, format=format),
        'bookmarks': reverse('bookmark_list', request=request, format=format)
    })

class TagList(generics.ListCreateAPIView):
    """
    List all tags, or create a new tag
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class TagDetails(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update or delete a Tag
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadonly)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class BookmarkList(generics.ListCreateAPIView):
    """
    List all tags, or create a new tag
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadonly)
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BookmarkDetails(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update or delete a Tag
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadonly)
    queryset = Bookmark.objects.all()
    serializer_class = BookmarkSerializer

class UserList(generics.ListCreateAPIView):
    """
    List all users, or create a new user
    """
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetails(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update or delete a user
    """
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserToken(APIView):
    """
    manage user api token
    """

    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    def get_obj(self, pk):
        try:
            user = User.objects.get(pk=pk)
            return Token.objects.get(user=user)
        except (Token.DoesNotExist, User.DoesNotExist):
            raise Http404

    def get(self, request, pk, format=None):
        """
        Get user token
        """
        token = self.get_obj(pk)
        return Response(TokenSerializer(token).data)

    def post(self):
        """
        post to create user token
        """
        pass
