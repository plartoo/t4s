from django.contrib import admin
from campaigns.models import Campaign, TaskQueue

admin.site.register(Campaign)
admin.site.register(TaskQueue)