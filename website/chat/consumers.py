import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


@database_sync_to_async
def is_student(user, course_id):
    """True if user is enrolled in the course (mirrors the room view)."""
    try:
        user.courses_joined.get(id=course_id)
        return True
    except Exception:
        return False


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        self.id = self.scope['url_route']['kwargs']['course_id']
        # Auth gate: reject anonymous clients (view gates the page, but
        # the websocket is reachable directly by URL). close() before
        # accept() makes the ASGI server reject the handshake.
        if not self.user.is_authenticated:
            await self.close(code=4401)
            return
        # Student gate: only enrolled students may join the room.
        if not await is_student(self.user, self.id):
            await self.close(code=4403)
            return
        self.room_group_name = f'chat_{self.id}'
        # присоединиться к группе чат-комнаты
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if getattr(self, 'room_group_name', None):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive(self, text_data):
        now = timezone.now()
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        avatar_url = self.user.avatar.url if self.user.avatar else None

        await self.channel_layer.group_send(
            self.room_group_name, {'type': 'chat_message',
                                   'message': message,
                                   'user': self.user.username,
                                   'datetime': now.isoformat(),
                                   'avatar': avatar_url}
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))