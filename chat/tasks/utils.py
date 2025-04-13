from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from chat.models import Message

def send_fallback_message(bot_user, conversation, text):
    message = Message.objects.create(
        conversation=conversation,
        sender=bot_user,
        encrypted_content=text,
        is_ai_generated=True
    )

    # Send via WebSocket
    channel_layer = get_channel_layer()
    group_name = f'chat_{conversation.id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'chat_message',
            'message': message.encrypted_content,
            'sender': bot_user,  # send the actual User object
            'message_id': message.id,
            'timestamp': message.created_at.isoformat(),
        }
    )

    return "Fallback message sent"
