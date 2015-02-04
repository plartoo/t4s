from django.db import models
from django.contrib.auth.models import User
from campaigns.constants import APPROVED, PENDING, SENT, SENDING
from smsmessages.models import Message
from organizations.models import Group
from campaigns.utils import collect_tree_content

class Campaign(models.Model):
    """
    """
    STATUS_CHOICES = (
        (APPROVED, 'Approved'),
        (PENDING, 'Pending'),
    )

    title = models.CharField('Conversation Title', max_length=500)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewer = models.ForeignKey(User, related_name='reviewed_campaign', null=True, blank=True)
    composer = models.ForeignKey(User, related_name='created_campaign')
    root_message =  models.ForeignKey(Message, related_name='root_message', null=True, blank=True)
    keywords = models.TextField(blank=True)

    def __unicode__(self):
        return self.title

    def update_search_keywords(self):
        if self.root_message:
            self.keywords = self.title + collect_tree_content(self.root_message)
        else:
            self.keywords = self.title + ' ' # if conversation doesn't have any message created yet

        self.save()

class TaskQueue(models.Model):
    STATUS_CHOICES = (
        (SENT, 'Sent'),
        (SENDING, 'Sending'),
        (PENDING, 'Pending'),
    )
    campaign = models.ForeignKey(Campaign)
    launch_time = models.DateTimeField()
    # ManytoMany means a group can belong to several TaskQ and TaskQ can contain several groups
    groups = models.ManyToManyField(Group)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=PENDING) # pending, sent
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)
