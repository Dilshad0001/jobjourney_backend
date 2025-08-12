from django.db import models
from django.conf import settings

class Message(models.Model):
    sender_id = models.IntegerField()
    receiver_id = models.IntegerField()
    content = models.TextField(blank=True)
    file = models.FileField(upload_to="chat_files/", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']




class ChatContact(models.Model):
    id=models.BigAutoField(primary_key=True)
    user_id = models.IntegerField()
    contact_id = models.IntegerField()
    contact_name=models.CharField(max_length=100,default='Unknown')
    unread_message_count=models.IntegerField(default=0)
    # last_message_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user_id', 'contact_id')  

    def __str__(self):
        return f"{self.user_id} ↔ {self.contact_id}"
    