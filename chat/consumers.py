import json
from django.utils import timezone
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from chat.models import Conversation, Message, Participant


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversation_id = None
        self.room_group_name = None

    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        # Check if user is authenticated and is a participant in the conversation
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
            return

        # Verify user is a participant
        is_participant = await self.is_participant(user.id, self.conversation_id)
        if not is_participant:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Update user's online status
        await self.update_user_status(user.id, True)

        await self.accept()

    async def disconnect(self, code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Update user's online status
        user = self.scope['user']
        if not user.is_anonymous:
            await self.update_user_status(user.id, False)

    @database_sync_to_async
    def is_participant(self, user_id, conversation_id):
        return Participant.objects.filter(
            user_id=user_id,
            conversation_id=conversation_id
        ).exists()

    @database_sync_to_async
    def save_message(self, user_id, conversation_id, encrypted_content):
        message = Message.objects.create(
            conversation_id=conversation_id,
            sender_id=user_id,
            encrypted_content=encrypted_content
        )

        # Update conversation's last update time
        conversation = Conversation.objects.get(id=conversation_id)
        conversation.updated_at = timezone.now()
        conversation.save()

        return message

    @database_sync_to_async
    def save_reaction(self, user_id, message_id, reaction):
        from .models import Reaction
        Reaction.objects.create(
            message_id=message_id,
            user_id=user_id,
            reaction=reaction
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'message')

        if message_type == 'message':
            # Store the encrypted message
            message = await self.save_message(
                user_id=self.scope['user'].id,
                conversation_id=self.conversation_id,
                encrypted_content=data['message']
            )

            # Forward to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': data['message'],
                    'sender_id': self.scope['user'].id,
                    'sender_username': self.scope['user'].username,
                    'message_id': message.id,
                    'timestamp': message.created_at.isoformat()
                }
            )

        elif message_type == 'typing':
            # Forward typing indicator
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'user_id': self.scope['user'].id,
                    'username': self.scope['user'].username,
                    'is_typing': data['is_typing']
                }
            )

        elif message_type == 'reaction':
            # Handle reaction
            await self.save_reaction(
                user_id=self.scope['user'].id,
                message_id=data['message_id'],
                reaction=data['reaction']
            )

            # Forward to the group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_reaction',
                    'message_id': data['message_id'],
                    'user_id': self.scope['user'].id,
                    'username': self.scope['user'].username,
                    'reaction': data['reaction']
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp']
        }))

    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing']
        }))

    async def message_reaction(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reaction',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
            'username': event['username'],
            'reaction': event['reaction']
        }))

    @database_sync_to_async
    def update_user_status(self, user_id, is_online):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=user_id)
        user.is_online = is_online
        user.last_activity = timezone.now()
        user.save()
