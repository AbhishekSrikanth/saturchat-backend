from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Create default admin user if it doesn't exist"

    def handle(self, *args, **kwargs):
        username = 'admin'
        email = 'admin@saturchat.com'
        password = 'admin'

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f"Admin user '{username}' created!"))
        else:
            self.stdout.write(f"Admin user '{username}' already exists.")
