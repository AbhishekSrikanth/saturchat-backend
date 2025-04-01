from django.db.models.signals import post_save
from django.dispatch import receiver
from chat.models import Message
from .tasks import process_ai_message_task

@receiver(post_save, sender=Message)
def handle_new_message(sender, instance, created, **kwargs):
    """
    Handle new messages - trigger AI processing if needed.
    """
    if created and not instance.is_ai_generated:
        conversation = instance.conversation
        if conversation.has_ai:
            # Process this message with the AI
            process_ai_message_task.delay(
                conversation_id=conversation.id,
                message_id=instance.id
            )
