from rest_framework import serializers
from .models import Message,ChatContact
from django.utils.timezone import localtime

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "sender_id", "receiver_id", "content","file", "timestamp", "is_read"]



class ChatContactserialser(serializers.ModelSerializer):
    last_message_at = serializers.SerializerMethodField()
    def get_last_message_at(self, obj):
        return localtime(obj.last_message_at).strftime('%Y-%m-%d %I:%M %p')
    class Meta:
        model=ChatContact
        fields=["id","user_id","contact_id","last_message_at","contact_name",'unread_message_count']





