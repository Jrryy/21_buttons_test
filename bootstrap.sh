#!/usr/bin/env sh

set -u
set -e

cd /code

# Wait for database
echo "Waiting for postgresql..."
until nc -z ${POSTGRES_HOST} ${POSTGRES_PORT}
do
  sleep 1
done
sleep 1

./manage.py migrate --noinput
./manage.py collectstatic --noinput

./manage.py runserver "0.0.0.0:8000"
