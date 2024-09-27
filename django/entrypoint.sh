#!/bin/sh

if [ "$POSTGRES_HOST" = "postgresql" ] # When env are set
then
    echo "Waiting for postgres..."
    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do # Test connexion to postgres
        sleep 0.1
    done
    echo "Postgres started"
fi

python3 manage.py flush --no-input
python3 manage.py migrate

exec "$@"
