import random
import re

from twilio.rest import TwilioRestClient
from twilio import TwilioRestException

from django.core.cache import cache
from django.conf import settings

def send_verification_code(to_num):
    client = TwilioRestClient(settings.T4S_TWILIO_SID, settings.T4S_TWILIO_TOKEN)
    rand_num = random.randrange(10000, 99999)
    msg_content = "This is your verfication code for Text4Strength: " + str(rand_num)
    msg_content += ". It will expire in five minutes, so please go ahead and complete the registration." 

    cache.set(to_num, rand_num, 300)

    try:
        client.sms.messages.create(body=msg_content, to=to_num, from_=settings.T4S_TWILIO_NUMBER)
    except TwilioRestException:
        return False
    return True

def get_user_role(user):
    person = None
    for role in ['student', 'advisor', 'researcher']:
        try:
            person = getattr(user, role)
            break
        except:
            pass
    return person

def format_to_phone_num(num_str):
    # Insert commas in thousandth places for every digit EXCEPT the last one, then
    # replace commas with dashes and then finally, add the last digit that was
    # excluded back
    phone_num_len = len(num_str)
    if (phone_num_len == 10):
        pattern=re.compile(r'^\D*(\d{3})\D*(\d{3})\D*(\d{4})\D*$')        
        formatted_num = '-'.join(pattern.search(num_str).groups())
    elif ((phone_num_len > 10) and (phone_num_len <= 13)):
        pattern=re.compile(r'^\D*(\d{1,3})\D*(\d{3})\D*(\d{3})\D*(\d{4})\D*$')
        formatted_num = '-'.join(pattern.search(num_str).groups())
    elif ((phone_num_len > 13) and (phone_num_len <= 15)):
        pattern=re.compile(r'^\D*(\d{1,2})\D*(\d{3})\D*(\d{3})\D*(\d{3})\D*(\d{4})\D*$')
        formatted_num = '-'.join(pattern.search(num_str).groups())
    else:   # Probably raise error; Not sure
        formatted_num = num_str

    return formatted_num
    