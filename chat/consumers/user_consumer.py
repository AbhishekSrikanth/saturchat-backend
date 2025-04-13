import json
from channels.generic.websocket import AsyncWebsocketConsumer

class UserConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_name = None

    async def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
            return

        self.group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def conversation_updated(self, event):
        await self.send(text_data=json.dumps({
            "type": "conversation_updated",
            "conversation_id": event["conversation_id"],
        }))
