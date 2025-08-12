import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import requests
from urllib.parse import parse_qs
from django.core.cache import cache
from django.utils import timezone
from django.utils.timezone import now


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        query_string = self.scope["query_string"].decode()
        self.token = parse_qs(query_string).get("token", [None])[0]
        self.user_id = self.scope['url_route']['kwargs']['user_id']

        cache.set(f"user_{self.user_id}_online", True, timeout=None)

        self.group_name = f"user_{self.user_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({"message": "Connected"}))
        await self.notify_contacts_online_status(True)


    async def disconnect(self, close_code):
        cache.set(f"user_{self.user_id}_online", False, timeout=None)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.notify_contacts_online_status(False)

    async def receive(self, text_data):
        from chat.models import ChatContact, Message

        data = json.loads(text_data)

        print("Received data===================:", data)

        if data.get("type") == "check_online":
            target_user_id = int(data.get("target_user_id"))
            is_online = cache.get(f"user_{target_user_id}_online", False)

            await self.send(text_data=json.dumps({
                "type": "online_status_response",
                "user_id": target_user_id,
                "is_online": is_online
            }))
            return  


        sender_id = int(data["sender_id"])
        receiver_id = int(data["receiver_id"])
        content = data.get("content", "")
        msg = await database_sync_to_async(Message.objects.create)(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content
        )
        await database_sync_to_async(self.ensure_contact_exists)(sender_id, receiver_id)

        await self.channel_layer.group_send(
            f"user_{receiver_id}",
            {
                "type": "chat_message",
                "sender_id": sender_id,
                "content": content,
                "timestamp": str(msg.timestamp),
                "new_contact": True ,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    def ensure_contact_exists(self, sender_id, receiver_id):




        from chat.models import ChatContact
        token=self.token
        actual_data = None
        if token:
            try:
                response = requests.get(
                    'http://api_gateway/auth/api/auth/self-profile/',
                    headers={'Authorization': f'Bearer {token}' }            )
                data=response.json()
                actual_data=data["data"]

            except requests.exceptions.RequestException as e:
                print("Error calling internal API:", e)

        else:
            print("⚠️ No Authorization token found in headers")    

        contact_obj, created = ChatContact.objects.get_or_create(
            user_id=receiver_id,
            contact_id=sender_id,
            defaults={
                "contact_name": actual_data.get("full_name", "Unknown"),
                "unread_message_count": 0
            }
        )
       
        contact_obj.unread_message_count += 1  
        contact_obj.last_message_at = timezone.now()
        contact_obj.save()

        print("📅 Django now():", now())
        print("🕒 Timezone.now():", timezone.now())

        try:
            sender_obj = ChatContact.objects.get(user_id=sender_id, contact_id=receiver_id)
            sender_obj.last_message_at = timezone.now() 
            sender_obj.save() 
        except ChatContact.DoesNotExist:
            pass

    async def notify_contacts_online_status(self, is_online: bool):
        from chat.models import ChatContact

        contacts = await database_sync_to_async(
            lambda: list(ChatContact.objects.filter(user_id=self.user_id))
        )()

        for contact in contacts:
            await self.channel_layer.group_send(
                f"user_{contact.contact_id}",
                {
                    "type": "online_status",  
                    "user_id": self.user_id,
                    "is_online": is_online,
                }
            )

    async def online_status(self, event):
        await self.send(text_data=json.dumps({
            "type": "online_status",
            "user_id": event["user_id"],
            "is_online": event["is_online"]
        }))



    # async def check_online_status(self, user_id_to_check):
    #     is_online = cache.get(f"user_{user_id_to_check}_online", False)
    #     return is_online
    

 

