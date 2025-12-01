# notifications/consumers.py
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

class NotificationsConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        qs = parse_qs(self.scope["query_string"].decode())
        token = qs.get("token", [None])[0]

        user = await self.get_user_from_jwt(token)
        if user:
            self.user = user
            self.group_name = f"user_{user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        action = content.get("action")
        if action == "mark_read":
            nid = content.get("notification_id")
            await self.mark_read(nid, self.user.id)

    async def notify(self, event):
        # called by channel_layer.group_send with payload in event["payload"]
        await self.send_json(event["payload"])

    @database_sync_to_async
    def get_user_from_jwt(self, token):
        """
        Validate JWT and return User instance or None.
        This supports:
          - djangorestframework-simplejwt tokens (preferred)
          - fallback to pyjwt decode with SECRET_KEY if simplejwt not installed

        The token param may be:
          - raw JWT: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
          - "Bearer <token>" — 'Bearer ' prefix will be removed
        """
        if not token:
            return None

        # strip Bearer prefix if present
        if token.startswith("Bearer "):
            token = token.split(" ", 1)[1]

        # Lazy imports to avoid app registry issues
        try:
            # try Simple JWT first
            from rest_framework_simplejwt.tokens import UntypedToken
            from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
            from django.contrib.auth import get_user_model
            from django.conf import settings
            import jwt
        except Exception:
            # If imports fail, return None
            return None

        User = get_user_model()

        # Try validating Simple JWT token (works for access & refresh but we only need user identity)
        try:
            UntypedToken(token)  # raises if invalid
            # If valid, decode to get user id (assume 'user_id' or 'user' claim)
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_signature": False})
            # simplejwt typically puts user_id in 'user_id' claim
            user_id = decoded.get("user_id") or decoded.get("user") or decoded.get("sub")
            if not user_id:
                return None
            try:
                return User.objects.get(id=user_id)
            except User.DoesNotExist:
                return None
        except Exception:
            # Fallback: try plain JWT decode using SECRET_KEY (some setups use plain JWT)
            try:
                decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = decoded.get("user_id") or decoded.get("user") or decoded.get("sub")
                if not user_id:
                    return None
                try:
                    return User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return None
            except Exception:
                return None

    @database_sync_to_async
    def mark_read(self, nid, user_id):
        # lazy import model here
        try:
            from .models import Notification
            n = Notification.objects.get(id=nid, user_id=user_id)
            n.is_read = True
            n.save()
        except Exception:
            # ignore silently if not found or other issues
            pass