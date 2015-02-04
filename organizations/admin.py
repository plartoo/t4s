from django.contrib import admin
from organizations.models import School
from organizations.models import Group

admin.site.register(School)
admin.site.register(Group)