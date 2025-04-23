#!/bin/sh

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create admin and bot users
python manage.py create_admin
python manage.py create_bots

# Start the Django server
daphne -b 0.0.0.0 -p 8000 saturchat.asgi:application
