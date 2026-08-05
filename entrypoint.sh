#!/usr/bin/env bash
set -e

echo "Starting entrypoint script..."
# Wait for DB if necessary (simple retry)
if [ -n "$DATABASE_URL" ]; then
  echo "Waiting for database..."
  n=0
  until python manage.py showmigrations > /dev/null 2>&1 || [ $n -ge 10 ]; do
    n=$((n+1))
    echo "Waiting for DB ($n/10)..."
    sleep 3
  done
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn shiva_shakti.wsgi --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-3} --log-file -
