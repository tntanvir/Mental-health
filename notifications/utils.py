from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Notification

User = get_user_model()


def send_notification(user,title: str, data=None):
    data = data or {}
    channel_layer = get_channel_layer()
    user = User.objects.get(id=user.id)

    notif = Notification.objects.create(
            user=user,
            title=title,
            data=data,
        )

    async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",               
            {
                "type": "notify",           
                "payload": {
                    "id": notif.id,
                    "title": notif.title,
                    "data": notif.data,
                    "is_read": notif.is_read,
                    "created_at": notif.created_at.isoformat(),
                },
            },
        )
