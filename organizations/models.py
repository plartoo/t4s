from django.db import models
from django.contrib.auth.models import User
from organizations.constants import DEFAULT_HELPINFO

# Create your models here.
class School(models.Model):
    name = models.CharField("School Name", max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    contacts = models.TextField(default='')
    help_reply = models.CharField(max_length=160, default=DEFAULT_HELPINFO)

    def __unicode__(self):
        return self.name

class Group(models.Model):
    name = models.CharField("Group Name", max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)

    def __unicode__(self):
        return self.name
