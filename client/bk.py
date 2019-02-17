#!/usr/bin/env python
## bk.py, client for booklets
import tempfile
import subprocess
import tabulate
import requests
import click
import json
import os
from pathlib import Path
from prompt_toolkit import prompt

template = """# insert bookmark url here
url: {}

title: {}

# insert tags here
tags: {}

# everything after are comments
comment:{}"""

editor = os.environ.get("EDITOR", "") or "vim"
def assert_code(res, code):
    if res.status_code != code:
        raise Exception("bad return code {} from server\nServer content{}".format(res.status_code, res.text))

def parse_content(fname):
    """parse content from stream"""
    stream = open(fname)
    data = {}
    in_comments = False
    while True:
        line = stream.readline()
        if not line: break

        if in_comments:
            data["comments"] += line
        line = line.rstrip("\n")
        if line.startswith("#") or line == "":
            continue

        kv = line.split(":", 1)
        if len(kv) == 2:
            if kv[0] in ["url", "title"]:
                data[kv[0].strip()] = kv[1].strip()
                continue
            if kv[0] == "tags":
                data[kv[0].strip()] = [i.strip() for i in kv[1].split(",")]
                continue
            if kv[0] == "comment":
                data[kv[0].strip()] = kv[1].strip()
                in_comments = True
    if not data["url"]:
        return False
    return data

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
        res = self.client.post(self.get_server("/bookmarks/"), data=data,
                               headers={"Authorization": "token {}".format(self.config.token)})
        assert_code(res, 201)
        click.echo(res.json())

    def update(self, _id, data):
        """update a bookmark """
        res = self.client.put(self.get_server("/bookmarks/{}/".format(_id)), data=data,
                              headers={"Authorization": "token {}".format(self.config.token)})
        assert_code(res, 200)
        click.echo(res.json())

    def delete(self, _id):
        """ delete bookmark"""
        res = self.client.delete(self.get_server("/bookmarks/{}/").format(_id),
                                 headers={"Authorization": "token {}".format(self.config.token)})
        assert_code(res, 204)
        click.echo(res.json())

    def create_user(self, username, email, password):
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        res = self.client.post(self.get_server("/users/"), data=data)
        assert_code(res, 201)
        uid = res.json()["id"]
        #auth = "Basic {}".format(base64.b64encode("{}:{}".format(username, password).encode()).decode())
        res = self.client.post(self.get_server("/users/{}/token/".format(uid)), data=data, auth=requests.auth.HTTPBasicAuth(username, password))
        assert_code(res, 201)
        return res.json()["token"]

    def get_server(self, path):
        server = self.config.server
        if not server:
            raise Exception("booklets server is not configured")
        return "{}/api{}".format(server, path)

    def get_bookmarks(self, tagorid):
        if tagorid.isdigit():
            path = "/bookmarks/{}/".format(tagorid)
        else:
            path = "/bookmarks/".format(tagorid)

        res = self.client.get(self.get_server(path), headers={"Authorization":
                                                              "token {}".format(self.config.token)})
        assert_code(res, 200)
        if tagorid.isdigit():
            return [res.json()]
        else:
            return [i for i in res.json()["results"] if tagorid in i["tags"]]

bk = BookletsClient(config)

@click.group()
def entry_point():
    config.load()

@click.command(name="refresh-token")
def refresh_token():
    pass

@click.command()
@click.argument("tagorid")
def show(tagorid):
    # list all bookmarks or under a tag
    data = bk.get_bookmarks(tagorid)
    table = [["id", "url", "tag(s)"]]
    for i in data:
        table.append([i["id"], i["url"], ",".join(i["tags"])])
    print(tabulate.tabulate(table, headers="firstrow"))

@click.command()
def new():
    # create a bookmark
    temp =  tempfile.NamedTemporaryFile(mode="w+")
    temp.write(template.format("", "", "", ""))
    temp.flush()
    while True:
        retcode = subprocess.call([editor, temp.name])
        if retcode != 0:
            raise Exception("editor returned non-zero code: {}".format(retcode))
        data = parse_content(temp.name)
        if not data:
            yes = prompt("bad data from file, continue to edit(y/n)?")
            if yes == "y":
                continue
            else:
                break
        else:
            bk.save(data)
            click.echo("bookmark created")
            break

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
            password1 = prompt("Password (again): ", is_password=True)
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
    click.echo("Your profile is saved at {}".format(config.path))

@click.command()
@click.argument("_id")
def edit(_id):
    """edit a bookmark"""
    bookmark = bk.get_bookmarks(_id)[0]
    temp =  tempfile.NamedTemporaryFile(mode="w+")
    temp.write(template.format(bookmark["url"], bookmark["title"],
                               ",".join(bookmark["tags"]),
                               bookmark["comment"]))
    temp.flush()
    while True:
        retcode = subprocess.call([editor, temp.name])
        if retcode != 0:
            raise Exception("editor returned non-zero code: {}".format(retcode))
        data = parse_content(temp.name)
        if not data:
            yes = prompt("bad data from file, continue to edit(y/n)?")
            if yes == "y":
                continue
            else:
                break
        else:
            bk.update(_id, data)
            click.echo("bookmark updated")
            break

@click.command()
@click.argument("_id")
def delete(_id):
    bookmark = bk.get_bookmarks(_id)[0]
    bk.delete(_id)
    click.echo("bookmark deleted")

entry_point.add_command(new)
entry_point.add_command(delete)
entry_point.add_command(init)
entry_point.add_command(show)
entry_point.add_command(edit)
entry_point.add_command(refresh_token)


if __name__ == "__main__":
    entry_point()
