from django.urls import re_path
from chat.consumers.chat_consumer import ChatConsumer
from chat.consumers.user_consumer import UserConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<conversation_id>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/user/(?P<user_id>\w+)/$', UserConsumer.as_asgi()),
]
