from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from twilio.rest import TwilioRestClient
from twilio import TwilioRestException
from smsmessages.models import MessageRecord
from smsmessages.constants import RETRY, GIVEUP, SUCCESS

class Command(BaseCommand):

    def handle(self, *args, **options):
        client = TwilioRestClient(settings.T4S_TWILIO_SID, settings.T4S_TWILIO_TOKEN)

        for record in MessageRecord.objects.filter(status=RETRY):
            try:
                twilio_reply = client.messages.create(body=record.content, to=record.receiver_num, from_=settings.T4S_TWILIO_NUMBER)
                record.twilio_msg_sid= twilio_reply.sid
                record.status = SUCCESS
                record.sent_at = datetime.now()
            except TwilioRestException, e:
                # log in MessageRecord here
                record.failed_times =  record.failed_times + 1
                
                if record.failed_times > settings.RETRY_LIMIT:
                    record.status = GIVEUP

            record.save()

