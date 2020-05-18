#!/usr/bin/env bash
set -e

RELOAD="";
if [ "$RELOAD_GUNICORN" == "true" ]; then
    RELOAD="--reload"
fi

cp /app/DjangoRestApi/.env.local /app/DjangoRestApi/.env
mkdir -p /app/locale

#This file needs to be at the top level, otherwise docker is not happy.
python /app/manage.py makemessages -d django -l ja -l en -l zh  --ignore "*node_modules*" --ignore "*site_packages*"
python /app/manage.py makemessages -d djangojs -l ja -l en -l zh --extension "jsx,tsx,js,ts"  --ignore "*node_modules*" --ignore "*site_packages*"
#python /app/manage.py compilemessages
python /app/manage.py migrate
python /app/manage.py collectstatic --no-input
exec gunicorn --chdir /app --workers 8 $RELOAD --bind 0.0.0.0:8000 DjangoRestApi.wsgi