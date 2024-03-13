from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from .models import Chat, ChatRoom
from django.contrib.auth.models import User
from buddysocial.models import Profile


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self):
        await self.channel_layer.group_discard(self.channel_layer, self.room_group_name)

    # Receiving Message
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender = data["sender"]
        receiver = data["receiver"]
        room = data["room"]

        await self.save_message(sender, receiver, message, room)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender,
                "receiver": receiver,
                "room": room,
            },
        )

    # Returning message to the frontend
    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]
        receiver = event["receiver"]
        room = event["room"]

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "sender": sender,
                    "receiver": receiver,
                    "room": room,
                }
            )
        )

    # Saving messages to the database
    @sync_to_async
    def save_message(self, sender, receiver, message, room):
        sender = User.objects.get(id=sender)
        receiver = User.objects.get(id=receiver)
        sender_profile = Profile.objects.get(user=sender)
        receiver_profile = Profile.objects.get(user=receiver)
        room = ChatRoom.objects.get(slug=room)
        Chat.objects.create(
            sender=sender, 
            receiver=receiver,
            sender_profile = sender_profile,
            receiver_profile = receiver_profile,
            room=room,
            message=message
        )
