from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()

class JWTAuthMiddleware(BaseMiddleware):
    async def get_user(self, user_id):
        try:
            return await User.objects.aget(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()

    async def __call__(self, scope, receive, send):
        token = None

        # Look for token in Sec-WebSocket-Protocol
        subprotocols = scope.get('subprotocols', [])
        if len(subprotocols) == 2 and subprotocols[0] == 'access_token':
            token = subprotocols[1]

        if token:
            try:
                validated = AccessToken(token)
                user = await self.get_user(validated['user_id'])
                scope['user'] = user
            except Exception:
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
