from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils.six import BytesIO
from rest_framework.authtoken.models import Token


class UserTest(TesTCase):
    username = "testUser"
    password = "thisispassword"

    def SetUp(self):
        ## setup user
        ## setup user token
        user = User(username=self.username)
        user.set_password(self.password)
        user.save()
        self.user = user
        token = Token.objects.create(user=user)
        token.save()

    def test_create_get_delete_users(self):
        data = {

        }

    def test_create_update_delete_user_token(self):
        pass

    def test_create_get_delete_tag(self):
        pass

    def test_create_get_update_delete_bookmarks(self):
        pass
