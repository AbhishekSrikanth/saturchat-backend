from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Message
from chat.tasks.ai import process_ai_message_task


@receiver(post_save, sender=Message)
def handle_new_message(sender, instance, created, **kwargs):
    """
    After a message is created, check if it mentions a bot.
    If so, queue the bot response task directly.
    """
    if not created or instance.is_ai_generated:
        return

    content = instance.encrypted_content.lower()
    conversation = instance.conversation

    try:
        bots = conversation.participants.filter(user__is_bot=True)
    except Exception:
        return

    for participant in bots:
        user = participant.user
        username = user.username.lower()

        if username == 'chatgpt' and '@chatgpt' in content:
            api_key = user.openai_api_key
            provider = 'openai'
        elif username == 'claude' and '@claude' in content:
            api_key = user.anthropic_api_key
            provider = 'anthropic'
        else:
            continue

        if api_key:
            process_ai_message_task.delay(
                conversation_id=conversation.id,
                message_content=instance.encrypted_content,
                user_id=user.id,
                ai_provider=provider,
                api_key_encrypted=api_key
            )
