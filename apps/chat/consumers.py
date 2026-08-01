import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        user = self.scope.get("user")

        if user is None or not user.is_authenticated:
            await self.close(code=4001) 
            return

        is_allowed = await self._user_can_access_room(user, self.room_id)
        if not is_allowed:
            await self.close(code=4003)  
            return

        self.user = user

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f"User {user.id} connected to chat room {self.room_id}")

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        message_body = content.get("message", "").strip()
        if not message_body:
            return

        message = await self._save_message(self.room_id, self.user, message_body)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message_id": message.id,
                "sender_id": self.user.id,
                "sender_email": self.user.email,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            },
        )

    async def chat_message(self, event):
        await self.send_json({
            "message_id": event["message_id"],
            "sender_id": event["sender_id"],
            "sender_email": event["sender_email"],
            "content": event["content"],
            "created_at": event["created_at"],
        })

    @database_sync_to_async
    def _user_can_access_room(self, user, room_id):
        from .models import ChatRoom
        try:
            room = ChatRoom.objects.select_related("contract").get(id=room_id)
        except ChatRoom.DoesNotExist:
            return False
        return room.is_participant(user)

    @database_sync_to_async
    def _save_message(self, room_id, user, content):
        from .models import ChatRoom, Message
        room = ChatRoom.objects.get(id=room_id)
        return Message.objects.create(room=room, sender=user, content=content)