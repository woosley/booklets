import base64
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils.six import BytesIO
from rest_framework.authtoken.models import Token


class UserTest(TestCase):
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
        self.client = Client()

    def test_create_get_delete_users(self):
        username = 'woosley.xu'
        password = 'password'
        data = {
            "email": "woosley@woosley.org",
            "first_name": "woosley",
            "last_name": "xu",
            "username": username,
            "password": password,
        }

        res = self.client.post("/api/users/", data)

        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.json()['username'], username)

        uid = res.json()['id']
        auth = "Basic {}".format(base64.b64encode("{}:{}".format(username, password).encode()).decode())
        res = self.client.get("/api/users/{}/".format(uid), HTTP_AUTHORIZATION=auth)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['username'], username)


    def test_create_update_delete_user_token(self):
        pass

    def test_create_get_delete_tag(self):
        pass

    def test_create_get_update_delete_bookmarks(self):
        pass
