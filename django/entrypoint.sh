#!/bin/sh

sleep 5 # making sure vault is operational

if [ "$POSTGRES_HOST" = "postgresql" ]
then
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
        sleep 1
    done
fi

python3 manage.py flush --no-input
python3 manage.py migrate

exec "$@"
