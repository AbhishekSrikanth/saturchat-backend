import json
from django.utils import timezone
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import Conversation, Message, Participant, Reaction
from chat.utils import user_object_to_dict


User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_id = None
        self.room_group_name = None

    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
            return

        is_participant = await self.is_participant(user.id, self.conversation_id)
        if not is_participant:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.update_user_status(user.id, True)
        await self.accept('access_token')

    async def disconnect(self, code):
        user = self.scope['user']
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        if not user.is_anonymous:
            await self.update_user_status(user.id, False)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        user_id = self.scope['user'].id
        user_info = await self.get_user_info(user_id)

        if data.get('type') == 'message':
            content = data['message']
            message = await self.save_message(user_id, self.conversation_id, data['message'])
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': content,
                    'sender': user_info,
                    'message_id': message.id,
                    'timestamp': message.created_at.isoformat(),
                }
            )

        elif data.get('type') == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'user': user_info,
                    'is_typing': data['is_typing'],
                }
            )

        elif data.get('type') == 'reaction':
            await self.save_reaction(user_id, data['message_id'], data['reaction'])
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_reaction',
                    'user': user_info,
                    'reaction': data['reaction'],
                    'message_id': data['message_id'],
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender': event['sender'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp'],
        }))

    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': event['user'],
            'is_typing': event['is_typing'],
        }))

    async def message_reaction(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reaction',
            'user': event['user'],
            'reaction': event['reaction'],
            'message_id': event['message_id'],
        }))


    @database_sync_to_async
    def is_participant(self, user_id, conversation_id):
        return Participant.objects.filter(user_id=user_id, conversation_id=conversation_id).exists()

    @database_sync_to_async
    def save_message(self, user_id, conversation_id, content):
        message = Message.objects.create(
            conversation_id=conversation_id,
            sender_id=user_id,
            content=content
        )
        conversation = Conversation.objects.get(id=conversation_id)
        conversation.updated_at = timezone.now()
        conversation.save()
        return message

    @database_sync_to_async
    def save_reaction(self, user_id, message_id, reaction):
        Reaction.objects.update_or_create(
            message_id=message_id,
            user_id=user_id,
            reaction=reaction
        )

    @database_sync_to_async
    def update_user_status(self, user_id, is_online):
        user = User.objects.get(id=user_id)
        user.is_online = is_online
        user.last_activity = timezone.now()
        user.save()

    @database_sync_to_async
    def get_user_info(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            return user_object_to_dict(user)
        except User.DoesNotExist:
            return {
                'id': None,
                'username': 'Unknown',
            }
