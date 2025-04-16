from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from chat.models import Message


def send_fallback_message(bot_user, conversation, text):
    Message.objects.create(
        conversation=conversation,
        sender=bot_user,
        encrypted_content=text,
        is_ai_generated=True
    )

    return "Fallback message sent"

def send_message_via_websocket(message):

    channel_layer = get_channel_layer()
    group_name = f'chat_{message.conversation.id}'

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'chat_message',
            'message': message.encrypted_content,
            'sender': user_object_to_dict(message.sender),
            'message_id': message.id,
            'timestamp': message.created_at.isoformat(),
        }
    )



def user_object_to_dict(user):
    """
    Convert a User object to a dictionary.
    """
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'avatar': user.avatar.url if user.avatar else None,
        'is_online': user.is_online,
        'last_activity': user.last_activity.isoformat() if user.last_activity else None,
    }
