from rest_framework import serializers
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from django.http import QueryDict

from .models import Bookmark, Tag


class TokenSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    class Meta:
        model = Token
        fields = ("user", "key", "created")

class UserSerializer(serializers.HyperlinkedModelSerializer):
    bookmarks = serializers.HyperlinkedIdentityField(
        many=True, view_name="bookmark_detail", read_only=True, format="html")

    class Meta:
        model = User
        fields = ("id", "username", "bookmarks", "first_name", "last_name",
                  "email", "password")
        extra_kwargs = {
            "password": {
                'write_only': True
            },
            "email": {
                "required": True
            }
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, user, validated_data):
        password = validated_data.get("password", None)
        if password:
            user.set_password(password)
            user.save()
        return user

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("name", )

class BookmarkSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True, read_only=True , slug_field="name")
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Bookmark
        fields = ("id", "title", "url", "comment", "tags", "added", "updated",
                  "user")

    def create(self, validated_data):
        initial_data = self.initial_data
        if isinstance(initial_data, QueryDict):
            tag_data = self.initial_data.getlist("tags", [])
        else:
            tag_data = self.initial_data.get("tags", [])

        bookmark = Bookmark.objects.create(**validated_data)
        for tag in tag_data:
            t, _ = Tag.objects.get_or_create(name=tag)
            bookmark.tags.add(t)
        return bookmark

    def update(self, bookmark, validated_data):
        initial_data = self.initial_data
        if isinstance(initial_data, QueryDict):
            tag_data = self.initial_data.getlist("tags", [])
        else:
            tag_data = self.initial_data.get("tags", [])

        bookmark.url = validated_data.get("url")
        bookmark.comment = validated_data.get("comment", "")
        bookmark.title = validated_data.get("title", "")

        # it seems that I can not use bookmark.tags.set() here
        for i in bookmark.tags.all():
            if i.name not in tag_data:
                bookmark.tags.remove(i)
        for tag in tag_data:
            t, _ = Tag.objects.get_or_create(name=tag)
            bookmark.tags.add(t)
        bookmark.save()
        return bookmark

    def validate_tags(self, value):
        return value
