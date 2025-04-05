#!/bin/sh

# Run migrations
python manage.py migrate

# Create admin user if it doesn't exist
echo "Checking if admin user exists..."
python manage.py shell << END
from accounts.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@saturchat.com', 'admin')
    print("Admin user created!")
else:
    print("Admin user already exists.")
END

# Start the Django server
daphne -b 0.0.0.0 -p 8000 saturchat.asgi:application
