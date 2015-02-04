'''
Created on Feb 14, 2014

@author: lacheephyo
'''
# Solution: we have to exclude all parents ids from the search
from smsmessages.models import MessageRecord
from twilio import TwilioRestException
from smsmessages.constants import RETRY

# Function below is used in messages/views.py
# to prevent us from creating circular message sequence
def get_parent_ids(msg):
    ids = [msg.id]
    options = msg.child_msg_options.all()
    if options:
        for option in options:
            ids.extend(get_parent_ids(option.parent_msg))
    return ids

def send_sms(client, msg_content, to_num, from_num, campaign=None, task_queue=None, root_msg=None):
    # TODO: we need to add 'sender' and 'receiver' in the future after we create Twilio user with fixtures
    # Note: we left out 'prompting_msg' because this is the sender portion; So it can be NULL as default
    record = MessageRecord(content=msg_content, message=root_msg, sender_num=from_num,
                           receiver_num=to_num, campaign=campaign, task_queue=task_queue)
    
    # TODO: This needs to be removed eventually because I'm only preliminarily testing whether
    # we can send SMS to both US and China from our system. 
    if ((len(to_num) > 10) and (to_num[:1] != "+")):
        to_num = "+" + to_num
    
    try:
        twilio_reply = client.messages.create(body=msg_content, to=to_num, from_=from_num)
        record.twilio_msg_sid= twilio_reply.sid
    except:
        # log in MessageRecord here
        record.status = RETRY
        record.failed_times = 1
        
    record.save()