#!/bin/bash

# Source of inspiration
# https://www.codingforentrepreneurs.com/blog/django-gunicorn-nginx-docker



# 1. Django app

# run database migrations if needed
python manage.py migrate --no-input

# collect static files
python manage.py collectstatic --no-input



# 2. gunicorn server

# run it as a daemon process (background)
gunicorn ces_project.wsgi:application --bind "127.0.0.1:8000" --daemon



# 3. nginx reverse proxy

# run it as a non-daemon process
nginx -g 'daemon off;'
