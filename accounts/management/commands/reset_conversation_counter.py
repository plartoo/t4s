import traceback

from django.core.management.base import BaseCommand

from accounts.models import Student, Advisor
from campaigns.utils import send_email_notification

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            for student in Student.objects.all():
                student.conversation_count_of_today = 0
                student.save()
                
            for advisor in Advisor.objects.all():
                advisor.conversation_count_of_today = 0
                advisor.save()

        except Exception, e:
            subject = "Error in resetting conversation counter: " + str(e)+ "failed"
            msg_body = traceback.format_exc()
            send_email_notification(subject, msg_body)
