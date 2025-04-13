from django.utils import timezone
from django.contrib.auth import get_user_model
from celery import shared_task

User = get_user_model()

@shared_task
def update_user_status():
    """
    Mark users as offline if they haven't been active for some time.
    """

    timeout = timezone.now() - timezone.timedelta(minutes=10)

    # Find users who are marked online but haven't been active
    inactive_users = User.objects.filter(
        is_online=True,
        last_activity__lt=timeout
    )

    inactive_users.update(is_online=False)

    return f"Updated status for {inactive_users.count()} users"
