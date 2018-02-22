# booklet

Personal bookmark service. 

This is because I didn't find a very good bookmark service suits my own need

there are 2 components in this repo. 

- a Django restful web service 
- a command line client

# status 

Somehow works

# Setup

## install
```
pip install -r requirements.txt
python manage.py makemigrations api
python manage.py migrate
```

## run

as a personal project, since there is no performance requirement, just run 

```
python manage.py runserver 0:$PORT
```

# Use
Check client (doc)[./client/README.md]
