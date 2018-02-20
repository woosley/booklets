## bk.py, client for booklets

import tempfile
import subprocess
import requests
import click
import json
import os
from pathlib import Path
from prompt_toolkit import prompt

template = """# insert bookmark url here
url:

title:

# insert tags here
tags:

# everything after are comments
comment:"""

class Config(object):

    path = Path.joinpath(Path.home(), ".booklets.json")

    def load(self):
        if os.path.exists(self.path) and os.path.isfile(self.path):
            config = json.load(open(self.path))
            self.server = config['server']
            self.username = config['username']
            self.token = config['token']
        else:
            self.server = False

    def save(self):
        with open(self.path, "w") as fh:
            fh.write(json.dumps({
                "server": self.server,
                "username": self.username,
                "token": self.token
            }, indent=4))
            fh.flush()


config = Config()


class BookletsClient(object):

    def __init__(self, config):
        self.config = config
        self.client = requests.Session()

    def save(self, data):
        "save data to bookmark server"
        tags = data['tags']
        pass

    def create_user(self, username, email, password):
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        res = self.client.post(self.get_server("/users/"), data=data)
        assert res.status_code == 201
        uid = res.json()["id"]
        #auth = "Basic {}".format(base64.b64encode("{}:{}".format(username, password).encode()).decode())
        res = self.client.post(self.get_server("/users/{}/token/".format(uid)), data=data, auth=requests.auth.HTTPBasicAuth(username, password))
        assert res.status_code == 201
        return res.json()["token"]

    def get_server(self, path):
        server = self.config.server
        if not server:
            raise Exception("booklets server is not configured")
        return "{}/api{}".format(server, path)


bk = BookletsClient(config)

@click.group()
def entry_point():
    config.load()

@click.command(name="refresh-token")
def refresh_token():
    pass

@click.command()
def show():
    pass

@click.command()
def new():
    # create a bookmark
    editor = "vim"
    temp =  tempfile.NamedTemporaryFile()
    temp.write(template.encode())
    temp.flush()
    while True:
        retcode = subprocess.call([editor, temp.name])
        if retcode != 0:
            raise Exception("editor returned non-zero code: {}".format(retcode))
        temp.seek(0)
        content = temp.read().decode()
        data = parse_content
        if not data:
            continue
        bk.save(data)

@click.command()
def init():
    # promote to get username, password, email etc
    config.server = prompt("Booklet server: ")
    while True:
        register = prompt("Create user on remote server(y/n)?")
        if register == "y":
            _new = True
        elif register == "n":
            _new = False
        else:
            continue
        break
    username = prompt("Username: ")
    if _new is True:
        email = prompt("Email: ")
        while True:
            password0 = prompt("Password: ", is_password=True)
            password1 = prompt("Password: ", is_password=True)
            if password0 == password1:
                break
            else:
                click.echo("Password do not match, continue ...")
        token = bk.create_user(username, email, password1)
    else:
        token = prompt("Access Token: ", is_password=True)
    config.username = username
    config.token = token
    config.save()


entry_point.add_command(new)
entry_point.add_command(init)
entry_point.add_command(refresh_token)


if __name__ == "__main__":
    entry_point()
