from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Create default bot users: @chatgpt and @claude"

    def handle(self, *args, **kwargs):
        bots = [
            {
                'username': 'chatgpt',
                'first_name': 'Chat',
                'last_name': 'GPT',
                'is_bot': True,
            },
            {
                'username': 'claude',
                'first_name': 'Claude',
                'last_name': 'AI',
                'is_bot': True,
            },
        ]

        for bot in bots:
            user, created = User.objects.get_or_create(
                username=bot['username'],
                defaults=bot
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created bot user: @{user.username}"))
            else:
                self.stdout.write(f"Bot user @{user.username} already exists")
