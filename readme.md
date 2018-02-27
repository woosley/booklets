# booklet 
[![Build Status](https://travis-ci.org/woosley/booklets.svg?branch=master)](https://travis-ci.org/woosley/booklets)[![codecov](https://codecov.io/gh/woosley/booklets/branch/master/graph/badge.svg)](https://codecov.io/gh/woosley/booklets)

Personal bookmark service. 

This is because I didn't find a very good bookmark service suits my own need

there are 2 components in this repo. 

- a Django restful web service 
- a command line client

# Status 

Somehow works. I don't really care about bugs or dirty code because I just need a small tool which is working

# Setup

## Install
```
pip install -r requirements.txt
python manage.py makemigrations api
python manage.py migrate
```

## Deploy

I don't want to use other webservices to deploy this small application. so

- [waitress](https://github.com/Pylons/waitress) is used to run the web server
- [whitenoise](http://whitenoise.evans.io/en/stable/index.html) is used to serve staticfiles


```
python manage.py collectstatic
python app.py
```

Now you can access http://localhost:8080 to browser the api

# Use
Check client [doc](./client/README.md)

```
(booklets) [root@localhost booklets]# bk.py show gz
  id  url                                                              tag(s)
----  ---------------------------------------------------------------  --------------
   7  http://gzlss.hrssgz.gov.cn/gzlss_web/business/tomain/main.xhtml  gz,life,shebao
```
