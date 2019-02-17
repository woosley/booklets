FROM python:3-alpine 
MAINTAINER woosley.xu<woosley.xu@gmail.com>
ADD . /booklets
WORKDIR /booklets
RUN  pip install -r requirements.txt &&  python manage.py makemigrations api && \
     python manage.py migrate

RUN  python  manage.py collectstatic
EXPOSE 8080
CMD ["python","app.py"]

