from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
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
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Update user's online status
        user = self.scope['user']
        if not user.is_anonymous:
            await self.update_user_status(user.id, False)
    
    