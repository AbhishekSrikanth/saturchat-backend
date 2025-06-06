import logging
from asgiref.sync import async_to_sync

from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from chat.models import Message
from chat.tasks.ai import process_ai_message_task
from chat.utils import send_message_via_websocket, notify_conversation_update

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Message)
def handle_new_message(sender, instance, created, **kwargs):
    if not created:
        return

    content = instance.content.lower()
    conversation = instance.conversation

    notify_conversation_update(conversation)

    if instance.is_ai_generated:
        send_message_via_websocket(instance)
        return

    try:
        bots = conversation.participants.filter(user__is_bot=True)
    except Exception:
        return

    # Find the admin user who should be the key holder
    admin_participant = conversation.participants.filter(is_admin=True).first()
    if not admin_participant:
        return

    admin_user = admin_participant.user

    for participant in bots:
        bot_user = participant.user
        username = bot_user.username.lower()

        if username == 'chatgpt' and '@chatgpt' in content:
            api_key = admin_user.openai_api_key
            provider = 'openai'
        elif username == 'claude' and '@claude' in content:
            api_key = admin_user.anthropic_api_key
            provider = 'anthropic'
        elif username == 'gemini' and '@gemini' in content:
            api_key = admin_user.gemini_api_key
            provider = 'gemini'
        else:
            continue

        process_ai_message_task.delay(
            conversation_id=conversation.id,
            message_content=instance.content,
            user_id=bot_user.id,
            ai_provider=provider,
            api_key=api_key
        )
