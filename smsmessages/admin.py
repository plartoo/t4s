from django.contrib import admin
from smsmessages.models import Message, MessageRecord, MessageOption

admin.site.register(Message)
admin.site.register(MessageRecord)
admin.site.register(MessageOption)