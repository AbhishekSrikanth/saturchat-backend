from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Message
from .tasks import process_ai_message_task


@receiver(post_save, sender=Message)
def handle_new_message(sender, instance, created, **kwargs):
    """
    After a message is created, trigger AI processing
    *only if* a known AI bot is mentioned and present in the conversation.
    """
    if not created or instance.is_ai_generated:
        return

    content = instance.encrypted_content.lower()

    if '@chatgpt' in content or '@claude' in content:
        process_ai_message_task.delay(
            conversation_id=instance.conversation_id,
            message_id=instance.id
        )
