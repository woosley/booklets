import os
from waitress import serve
from booklets.wsgi import application

port = os.environ.get("BOOKLET_PORT", None) or 8080
port = int(port)
if __name__ == '__main__':
    serve(application, port=port)
