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
    """
    Process messages sent in conversations with AI integrations.
    """

    try:
        message = Message.objects.get(id=message_id)
        conversation = Conversation.objects.get(id=conversation_id)

        if not conversation.has_ai:
            return "Conversation has no AI"

        # Find the user who owns the API key
        owner = conversation.participants.filter(is_admin=True).first()
        if not owner:
            return "No admin found for AI conversation"

        # Get the appropriate API key
        if conversation.ai_provider == 'openai':
            api_key_encrypted = owner.user.openai_api_key
        elif conversation.ai_provider == 'anthropic':
            api_key_encrypted = owner.user.anthropic_api_key
        else:
            return f"Unsupported AI provider: {conversation.ai_provider}"

        if not api_key_encrypted:
            return "No API key found"

        # Process the message asynchronously
        process_ai_message.delay(
            conversation_id=conversation_id,
            message_content=message.encrypted_content,
            user_id=owner.user.id,
            ai_provider=conversation.ai_provider,
            api_key_encrypted=api_key_encrypted
        )

        return "AI message processing started"

    except (Message.DoesNotExist, Conversation.DoesNotExist) as e:
        return f"Error: {str(e)}"
