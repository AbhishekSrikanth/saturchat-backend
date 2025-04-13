from chat.models import Message

def send_fallback_message(bot_user, conversation, text):
    return Message.objects.create(
        conversation=conversation,
        sender=bot_user,
        encrypted_content=text,
        is_ai_generated=True
    )
