from rest_framework import serializers
import json
from django.contrib.auth.models import User

from .models import Bookmark, Tag

class UserSerializer(serializers.HyperlinkedModelSerializer):
    bookmarks = serializers.HyperlinkedIdentityField(many=True, view_name="bookmark_detail", read_only=True, format="html")
    email = serializers.Field(required=True, source="user.email")


    class Meta:
        model = User
        fields = ("id", "username", "bookmarks", "first_name", "last_name", "email", "password")
        extra_kwargs = {
            "password": {'write_only': True}
        }


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("name",)


class BookmarkSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name")
    user = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Bookmark
        fields = ("id", "title", "url", "comment", "tags", "added", "updated", "user")

    def create(self, validated_data):
        # Slugfield will create the mapping only if the target field exists already,
        # override create function to create new tags on the fly

        # Tags field is readonly, get tag values from initial_data
        tag_data = self.initial_data.get("tags", [])
        bookmark = Bookmark.objects.create(**validated_data)
        for tag in tag_data:
            t, _ = Tag.objects.get_or_create(name=tag)
            bookmark.tags.add(t)
        return bookmark

    def update(self, bookmark, validated_data):
        # Tags field is readonly, get tag values from initial_data
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
