from django.db import models
from django.contrib.auth.models import User
from organizations.models import School
from accounts.constants import PEERLEADER, STUDENTMEMBER
from accounts.utils import format_to_phone_num

# goal: classify User as "students", "researcher", "teacher/advisor" or "leader"
# student, researcher, advisors, leaders
class Student(models.Model):
    ROLE_CHOICES = (
        (PEERLEADER, 'Peer Leader'),
        (STUDENTMEMBER, 'Student Member'),
    )
    
    user = models.OneToOneField(User)
    groups = models.ManyToManyField('organizations.Group')
    school = models.ForeignKey(School)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default=STUDENTMEMBER)
    conversation_limit_per_day = models.IntegerField(default=5)
    conversation_count_of_today = models.IntegerField(default=0)

    def get_formatted_phone_number(self):
        return format_to_phone_num(self.user.username)


class Advisor(models.Model):
    user = models.OneToOneField(User)
    groups = models.ManyToManyField('organizations.Group')
    school = models.ForeignKey(School)
    conversation_limit_per_day = models.IntegerField(default=100)
    conversation_count_of_today = models.IntegerField(default=0)

    def get_formatted_phone_number(self):
        return format_to_phone_num(self.user.username)

class Researcher(models.Model):
    user = models.OneToOneField(User)
    phone = models.CharField(max_length=16, blank=True)
    conversation_limit_per_day = models.IntegerField(default=100000)
    conversation_count_of_today = models.IntegerField(default=0)

    def get_formatted_phone_number(self):
        return format_to_phone_num(self.user.username)
