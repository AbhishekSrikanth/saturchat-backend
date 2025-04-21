from django.conf import settings
from django.utils import timezone
from celery import shared_task
from chat.models import Message

@shared_task
def clean_old_messages(days=30):
    """
    Periodically clean old messages to save storage space.
    Only runs if CLEAN_OLD_MESSAGES setting is True.
    """

    if not getattr(settings, 'CLEAN_OLD_MESSAGES', False):
        return

    cutoff_date = timezone.now() - timezone.timedelta(days=days)
    old_messages = Message.objects.filter(created_at__lt=cutoff_date)

    # Keep metadata, but clear message content
    old_messages.update(content="[Expired Message]")

    return f"Cleaned {old_messages.count()} old messages"
