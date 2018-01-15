#!/bin/sh
cd newsorg
python3 manage.py makemigrations 
python3 manage.py migrate 
python3 manage.py collectstatic --noinput
uwsgi --master --socket 0.0.0.0:8000 --plugins python3 --protocol uwsgi --wsgi newsorg.wsgi:application
exec "$@"
