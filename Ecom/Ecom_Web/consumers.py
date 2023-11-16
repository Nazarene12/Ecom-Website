from channels.generic.websocket import AsyncWebsocketConsumer
import json
# from Ecom_Web.models import Order
# from django.core.exceptions import ObjectDoesNotExist
# from asgiref.sync import sync_to_async

class NotificationChannel(AsyncWebsocketConsumer):
    

    async def connect(self): 
        print('s')
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        order_id = text_data_json['order_id']
        print('recived')
        # Here, you would typically send a message to the admin that an order has been placed.
        # For simplicity, we're just sending a message back to the client.
        await self.send(text_data=json.dumps({
            'order': True
        }))  



class AdminConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'admin_group'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # Send message to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'admin_message',
                'message': message
            }
        )

    async def admin_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))
