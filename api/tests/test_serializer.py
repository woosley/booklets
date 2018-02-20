# test api serializer

from django.test import TestCase
from django.utils.six import BytesIO
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from django.contrib.auth.models import User
from api.serializers import BookmarkSerializer, TagSerializer, UserSerializer
from api.models import Bookmark, Tag


class BookmarkSerializerTest(TestCase):

    tag = "linux"
    title = "ubuntu website"
    url="https://www.ubuntu.org"
    comment="ubuntu is the best linux distribution"

    def setUp(self):

        user = User(username="test")
        user.set_password("test123456")
        user.save()
        self.user = user
        t = Tag.objects.create(name=self.tag)
        b = Bookmark.objects.create(title=self.title, url=self.url, comment=self.comment, user=self.user)
        b.tags.add(t)
        b.save()
        self.b_id = b.id

    def test_dump_bookmarks(self):
        bks = Bookmark.objects.get(url=self.url)
        self.assertSequenceEqual(bks.title, self.title)
        b = BookmarkSerializer(instance=bks)
        self.assertEqual(b.data["tags"], [self.tag])
        self.assertEqual(b.data["title"], self.title)
        self.assertEqual(b.data["url"], self.url)
        self.assertEqual(b.data["comment"], self.comment)

    def test_save_bookmarks_with_tags(self):
        j = BytesIO(b'{"title": "Centos", "tags":["linux"], "url":"www.centos.org", "comment":"not bad"}')
        data = JSONParser().parse(j)
        b = BookmarkSerializer(data=data)
        self.assertTrue(b.is_valid())
        b.save(user=self.user)
        bks = Bookmark.objects.get(url="www.centos.org")
        self.assertSequenceEqual(bks.title, "Centos")

    def test_update_bookmark_add_tag(self):
        title = "test title"
        t = Tag.objects.create(name="ubuntu")
        t.save()
        data  = {"title": title, "url": self.url, "comment": self.comment, "tags": ["linux", "ubuntu"]}
        bks = Bookmark.objects.get(url=self.url)
        b = BookmarkSerializer(bks, data=data)
        self.assertTrue(b.is_valid())
        b.save()
        bks = Bookmark.objects.get(url=self.url)
        self.assertEqual(bks.title, title)
        self.assertTrue("ubuntu" in [i.name for i in bks.tags.all()])
        self.assertEqual(len(bks.tags.all()), 2)

    def test_update_bookmark_delete_tag(self):

        data  = {"title": self.title, "url": self.url, "comment": self.comment, "tags": []}
        bks = Bookmark.objects.get(url=self.url)
        b = BookmarkSerializer(bks, data=data)
        self.assertTrue(b.is_valid())
        b.save()
        bks = Bookmark.objects.get(url=self.url)
        self.assertEqual(len(bks.tags.all()), 0)

    def test_add_tags(self):
        tag = "Centos"
        data = {"name": tag}
        t = TagSerializer(data=data)
        self.assertTrue(t.is_valid())
        t.save()
        ts = Tag.objects.get(name=tag)
        self.assertTrue(ts.name == tag)

    def test_update_bookmark_with_new_tag(self):

        tags = ["Cnetos", "redhat", "linux"]
        data  = {"title": "forfun", "url": self.url, "comment": self.comment, "tags": tags}


        bks = Bookmark.objects.get(url=self.url)
        b = BookmarkSerializer(bks, data=data)
        self.assertTrue(b.is_valid())
        b.save()
        bks = Bookmark.objects.get(url=self.url)
        self.assertEqual(len(bks.tags.all()), 3)
        self.assertTrue("Cnetos" in [i.name for i in bks.tags.all()])


    def test_create_user(self):
        username = "thisisatestuser"
        password = "thisisatestpassword"
        d = {
            "username": username,
            "password": password,
            "email": "test@email.org"
        }
        u = UserSerializer(data=d)
        self.assertTrue(u.is_valid())
        u.save()

        user = User.objects.get(username=username)
        self.assertEqual(user.username, username)

    def test_get_user_bookmarks(self):
        user = User.objects.get(username=self.user.username)
        b = user.bookmarks.all()
        self.assertEqual(len(b), 1)
        self.assertEqual(b[0].title, self.title)

    def test_update_user(self):
        pass

    def test_update_user_password(self):
        pass
