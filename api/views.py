from .models import Tag, Bookmark
from rest_framework import generics
from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import permissions
from rest_framework import status
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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def delete(self, request, *args, **kwargs):
        return Response({"error": "delete on tag is not allowed"}, status=status.HTTP_400_BAD_REQUEST)


class BookmarkList(generics.ListCreateAPIView):
    """
    List all tags, or create a new tag
    """

    def get_queryset(self):
        user = self.request.user
        return Bookmark.objects.filter(user=user)

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadonly)
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

    #permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        return Response({"error": "listing users is not supported"}, status=status.HTTP_400_BAD_REQUEST)


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
            return Token.objects.get(user=self.get_user(pk))
        except Token.DoesNotExist:
            raise Http404

    def get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        """
        Get user token
        """
        token = self.get_obj(pk)
        return Response(TokenSerializer(token).data)

    def post(self, request, pk):
        """
        post to create user token
        """
        #just create user token directly
        user = self.get_user(pk)
        token, _new = Token.objects.get_or_create(user=user)
        # token.save gives me duplicated user_id
        if _new:
            token.save()
        else:
            token.delete()
            token = Token(user=user)
            token.save()
        return Response({"token": token.key}, status=status.HTTP_201_CREATED)
