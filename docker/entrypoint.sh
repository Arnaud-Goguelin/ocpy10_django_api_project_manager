#!/bin/sh

set -e

# Default values
# number of worker and threads:
# according to gunicorn docs (https://docs.gunicorn.org/en/stable/design.html#asyncio-workers)
# n workers should be equel to (2 x $num_cores) + 1

# according to Cambring (https://guidebook.devops.uis.cam.ac.uk/notes/gunicorn-tuning/)
# n workers X n tread shoudl be equal to 4


WORKERS=${WORKERS:-1}

echo "Starting application in $ENVIRONMENT mode..."

    echo "Starting background scheduler..."
    sh /usr/local/bin/scheduler.sh &

if [ "$ENVIRONMENT" = "local" ]; then
    echo "Running database migrations..."
    python manage.py migrate --noinput

    echo "Creating test users..."
    python manage.py create_test_users

    echo "Running Django local server..."
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "Running database migrations..."
    python manage.py migrate --noinput

    echo "Collecting static files..."
    python manage.py collectstatic --noinput

    echo "Running production server with uvicorn (workers: $WORKERS)..."
    exec uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --workers "$WORKERS"
fi
