from datetime import datetime

from django.core.management.base import BaseCommand
from campaigns.models import TaskQueue
from accounts.models import Student, Advisor
from django.conf import settings

from twilio.rest import TwilioRestClient
from campaigns.constants import PENDING, SENT, SENDING, FAILED
from smsmessages.utils import send_sms
from campaigns.utils import send_email_notification
import traceback

class Command(BaseCommand):

    def handle(self, *args, **options):
        now = datetime.now()
        pending_tasks = TaskQueue.objects.filter(status=PENDING, launch_time__lt=now)
        pending_tasks.update(status=SENDING)            # Set this to SENDING first to be safe, then if we fail to deliver message, set it back to PENDING in the following loop 
        
        tasks = TaskQueue.objects.filter(status=SENDING)

        client = TwilioRestClient(settings.T4S_TWILIO_SID, settings.T4S_TWILIO_TOKEN)

        for task in tasks:
            try:
                root_msg = task.campaign.root_message
                msg_content =  root_msg.get_full_content()
                
                for group in task.groups.all():
                    advisors = list(Advisor.objects.filter(groups=group))
                    students = list(Student.objects.filter(groups=group))
                    
                    for person in students+advisors:
                        # check the sms limitation
                        if person.conversation_limit_per_day > person.conversation_count_of_today:
                            to_num = person.user.username
                            from_num = settings.T4S_TWILIO_NUMBER
                            send_sms(client, msg_content, to_num, from_num, campaign=task.campaign, task_queue=task, root_msg=root_msg)
                            person.conversation_count_of_today += 1
                            person.save()

            except Exception, e:
                task.status = FAILED
                task.save()

                subject = "Task Error: " + str(e) + " for Task ID: " + str(task.id) + " and Title:" + task.campaign.title 
                msg_body = traceback.format_exc()
                send_email_notification(subject, msg_body)
                
            # update task status
            task.status = SENT
            task.save()


