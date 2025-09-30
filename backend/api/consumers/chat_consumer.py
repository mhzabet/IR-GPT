import json

from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user_id = str(self.scope['user'].id)
        self.channel_name_for_user = f"user_{self.user_id}"

        await self.channel_layer.group_add(
            self.channel_name_for_user, self.channel_name
        )

        await self.accept()
    async def disconnect(self, code):
        # leave the private group
        await self.channel_layer.group_discard(
            self.channel_name_for_user, self.channel_name
        )
    async def receive(self, text_data = None, bytes_data = None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        await self.channel_layer.group_send(
            self.channel_name_for_user, {"type":"chat.message", "message":message}
        )

    async def chat_message(self, event):
        message = event['message']            
        await self.send(text_data=json.dumps({"message": message}))
