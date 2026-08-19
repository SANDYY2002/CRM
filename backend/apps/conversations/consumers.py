from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Conversation


class ConversationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]

        if not self.user or self.user.is_anonymous:
            await self.close(code=4401)
            return

        if not await self.user_can_access():
            await self.close(code=4403)
            return

        self.group_name = f"conversation_{self.conversation_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send_json({"type": "connection.ready", "conversation_id": int(self.conversation_id)})

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get("type") == "typing":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "typing.event",
                    "user_id": self.user.id,
                    "is_typing": bool(content.get("is_typing", True)),
                },
            )

    async def typing_event(self, event):
        if event["user_id"] != self.user.id:
            await self.send_json({
                "type": "typing",
                "user_id": event["user_id"],
                "is_typing": event["is_typing"],
            })

    async def message_event(self, event):
        await self.send_json({"type": "message", "message": event["message"]})

    @database_sync_to_async
    def user_can_access(self):
        return Conversation.objects.filter(
            pk=self.conversation_id,
            organization__members=self.user,
        ).exists()
