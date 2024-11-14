#!/bin/sh

python3 manage.py set_site_domain
python3 manage.py migrate
python3 manage.py create_superuser

exec "$@"