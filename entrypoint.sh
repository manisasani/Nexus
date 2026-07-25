#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.5
done
echo "PostgreSQL is up."

if [ "$1" = "web" ] || [ -z "$1" ]; then
  echo "Applying database migrations..."
  python manage.py migrate --noinput

  echo "Collecting static files..."
  python manage.py collectstatic --noinput

  echo "Starting server..."
  exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
else
  echo "Starting: $@"
  exec "$@"
fi