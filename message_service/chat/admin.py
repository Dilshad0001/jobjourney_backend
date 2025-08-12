from django.contrib import admin

# Register your models here.

from .models import ChatContact,Message

admin.site.register(ChatContact)
admin.site.register(Message)
