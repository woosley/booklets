import base64
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils.six import BytesIO
from rest_framework.authtoken.models import Token


class UserTest(TestCase):
    username = "testUser"
    password = "thisispassword"

    def setUp(self):
        user = User(username=self.username)
        user.set_password(self.password)
        user.save()
        token = Token.objects.create(user=user)
        token.save()
        self.user = user
        self.client = Client()

    def test_create_get_update_delete_users(self):
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

        new_password = "fake1"
        data['password'] =  new_password

        res = self.client.put("/api/users/{}/".format(uid), data=json.dumps(data), content_type='application/json', HTTP_AUTHORIZATION=auth)
        self.assertEqual(res.status_code, 200)

        auth = "Basic {}".format(base64.b64encode("{}:{}".format(username, new_password).encode()).decode())
        res = self.client.delete("/api/users/{}/".format(uid), HTTP_AUTHORIZATION=auth)
        self.assertEqual(res.status_code, 204)

    def test_create_update_delete_user_token(self):
        auth = "Basic {}".format(base64.b64encode("{}:{}".format(self.username, self.password).encode()).decode())
        res = self.client.get("/api/users/{}/".format(self.user.id), HTTP_AUTHORIZATION=auth)
        self.assertEqual(res.status_code, 200)

        res = self.client.post("/api/users/{}/token/".format(self.user.id), HTTP_AUTHORIZATION=auth)
        self.assertEqual(res.status_code, 201)
        self.assertTrue("token" in res.json())
        token = res.json()["token"]

        auth = "token {}".format(token)
        res = self.client.get("/api/users/{}/".format(self.user.id), HTTP_AUTHORIZATION=auth)
        self.assertEqual(res.status_code, 200)

        res = self.client.post("/api/users/{}/token/".format(self.user.id), HTTP_AUTHORIZATION=auth)
        self.assertEqual(res.status_code, 201)
        self.assertTrue("token" in res.json())
        self.assertTrue(res.json()["token"] != token)

    def test_create_get_delete_tag(self):
        tag = "fistag"
        auth = "Basic {}".format(base64.b64encode("{}:{}".format(self.username, self.password).encode()).decode())
        data = {"name": tag}
        res = self.client.post("/api/tags/", data=data, HTTP_AUTHORIZATION=auth)
        self.assertTrue(res.status_code == 201)

        res = self.client.get("/api/tags/{}/".format(tag), HTTP_AUTHORIZATION=auth)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["name"] == tag)

    def test_create_get_update_delete_bookmarks(self):
        pass
