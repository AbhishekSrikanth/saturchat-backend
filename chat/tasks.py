from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model

from chat.models import Message, Conversation
from chat.ai_integration import process_ai_message

User = get_user_model()


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
    old_messages.update(encrypted_content="[Expired Message]")

    return f"Cleaned {old_messages.count()} old messages"


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


@shared_task
def process_ai_message_task(conversation_id, message_id):

    try:
        message = Message.objects.get(id=message_id)
        conversation = Conversation.objects.get(id=conversation_id)

        # Look for bot users among the participants
        bots = conversation.participants.filter(user__is_bot=True)

        for bot_participant in bots:
            user = bot_participant.user
            if user.username.lower() == 'chatgpt':
                api_key_encrypted = user.openai_api_key
                provider = 'openai'
            elif user.username.lower() == 'claude':
                api_key_encrypted = user.anthropic_api_key
                provider = 'anthropic'
            else:
                continue

            if api_key_encrypted:
                process_ai_message.delay(
                    conversation_id=conversation.id,
                    message_content=message.encrypted_content,
                    user_id=user.id,
                    ai_provider=provider,
                    api_key_encrypted=api_key_encrypted
                )

        return "Triggered AI tasks for available bots"

    except (Message.DoesNotExist, Conversation.DoesNotExist) as e:
        return f"Error: {str(e)}"
