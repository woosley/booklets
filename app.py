from waitress import serve
from booklets.wsgi import application

if __name__ == '__main__':
    serve(application, port=8001)
