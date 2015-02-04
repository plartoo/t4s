import re

from braces.views import LoginRequiredMixin, AjaxResponseMixin,\
    JsonRequestResponseMixin

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q

from smsmessages.forms import MessageUpdateForm
from smsmessages.models import Message, MessageOption, MessageRecord
from smsmessages.forms import AddOptionForm
from django.views.generic.base import View, TemplateView
from smsmessages.utils import get_parent_ids, send_sms
from campaigns.models import TaskQueue
from django.http.response import HttpResponse
from django.conf import settings
from twilio.rest import TwilioRestClient
from smsmessages.constants import DONT_UNDERSTAND, THANKYOU, FREERESPONSE
from django.contrib.auth.models import User
from organizations.constants import CONTACT_TEXT

class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'messages/list.html'
    
    # queryset is needed below because we only want to list the ones composed by the user
    def get_queryset(self):
        qs = super(MessageListView, self).get_queryset()
        return qs.filter(composer=self.request.user)

class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageUpdateForm # check "forms.py" wher e we restrict what info we show
    template_name = 'messages/update.html'
    success_url = reverse_lazy('smsmessages:list')

class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy('smsmessages:list')

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

class AddOptionView(LoginRequiredMixin, CreateView):
    model = MessageOption
    template_name = 'messages/options/create.html'
    form_class = AddOptionForm

    def get_success_url(self):
        if 'cam_id' in self.request.GET:
            cam_id = self.request.GET['cam_id']
            return '%s?cam_id=%s'%(reverse_lazy('campaigns:message_list'), cam_id)
            #return '{}?cam_id={}'.format(reverse_lazy('campaigns:message_list'), cam_id)
        return reverse_lazy('smsmessages:list')
        

    # the method below is to pass down parent_msg to template
    def get_context_data(self, **kwargs):
        data = super(AddOptionView, self).get_context_data(**kwargs)
        msg = Message.objects.get(id=self.request.GET['msg_id'])
        data['parent_msg'] = msg
        return data


    def get_form(self, form_class):
        msg = Message.objects.get(id=self.request.GET['msg_id'])
        return form_class(msg, **self.get_form_kwargs())
        

    # we need below because we excluded parent_message in the form
    def form_valid(self, form):
        option = form.save(commit=False)
        msg = Message.objects.get(id=self.request.GET['msg_id'])
        option.parent_msg = msg
        option.save()
        return super(AddOptionView, self).form_valid(form)

class MessageSearchView(LoginRequiredMixin, JsonRequestResponseMixin, AjaxResponseMixin, View):
    def get_ajax(self, request, *args, **kwargs):
        keyword = request.GET.get('keyword')
        parent_msg_id = request.GET['msg_id']
        parent_msg = Message.objects.get(id=parent_msg_id)
        parent_ids = get_parent_ids(parent_msg)
        # https://docs.djangoproject.com/en/dev/ref/models/querysets/#values-list
        # can be short for:
        # child_ids = [option.child_msg.id for option in parent_msg.options.all()]
        child_ids = []
        for option in parent_msg.options.all():
            child_ids.append(option.child_msg.id)
        
        excluded_ids_list = parent_ids + child_ids 
        msgs = Message.objects.exclude(id__in=excluded_ids_list).filter(content__icontains=keyword)[:10]
        msgs_json = [{'id': m.id, 'content': m.content} for m in msgs]
        return self.render_json_response(msgs_json)

class MessageReceiveView(View):
    def get(self, request, *args, **kwargs):
        client = TwilioRestClient(settings.T4S_TWILIO_SID, settings.T4S_TWILIO_TOKEN)

        # Twilio's GET request for incoming SMS looks like this:
        # "GET /smsmessages/receive?AccountSid=AC14415ab0be51ba4da097dd51da5a7d8f
        # &MessageSid=SMacc66709b7ba53144cd632b6ee17c0f0&Body=Ahhhhh&ToZip=14603
        # &ToCity=ROCHESTER&FromState=NY&ToState=NY&SmsSid=SMacc66709b7ba53144cd632b6ee17c0f0
        # &To=%2B15853600116&ToCountry=US&FromCountry=US&SmsMessageSid=SMacc66709b7ba53144cd632b6ee17c0f0
        # &ApiVersion=2010-04-01&FromCity=&SmsStatus=received&NumMedia=0&From=%2B15856268095&FromZip= HTTP/1.1" 404 2862

        # TODO ***: Refactor this and figure out a neater way to separate between country code and core phone num 
        # IMPORTANT: must get rid of the '+1' too
        
        #import ipdb
        #ipdb.set_trace()
        # TODO: This is a temporary hack; We need to decide on how to handle different country codes
        if ((request.GET['From'][:2] == "+1") and (len(request.GET['From'][2:]) == 10)): # means US number
            caller_num = request.GET['From'][2:]        # "5856261222" from "+15856261222"
        else:
            caller_num = request.GET['From'][1:]        #  "8613910988979" from "+8613910988979" 

        our_twilio_num = request.GET['To'][2:]      # our_twilio
        
        msg_content = request.GET['Body']
        sms_sid = request.GET['SmsSid']

        last_msg_record = MessageRecord.objects.filter(message__isnull=False, receiver_num=caller_num).last()
        last_msg_sent = last_msg_record.message
        task_queue = last_msg_record.task_queue
        campaign = last_msg_record.campaign     # For trigger keyword if user type 'A' vs. 'a', we need to cover this

        # check if student reply HELPINFO 
        matched_obj = re.match('helpinfo.*', msg_content, re.I|re.S)
        if matched_obj:
            try:
                school = User.objects.get(username=caller_num).student.school
            except:
                school = User.objects.get(username=caller_num).advisor.school

            response_msg = school.help_reply
            send_sms(client, response_msg, caller_num, our_twilio_num, root_msg=last_msg_sent)  # IMPORTANT: we must set root_msg so that if they type HELPINFO in the middle of a conversation, we still don't lose track of where they are
            return HttpResponse('OK')

        # check if student reply CONTACT 
        matched_obj = re.match('contact(.*)', msg_content, re.I|re.S)
        if matched_obj:
            try:
                school = User.objects.get(username=caller_num).student.school
            except:
                school = User.objects.get(username=caller_num).advisor.school
                
            for contact in school.contacts.split(','):
                response_msg = CONTACT_TEXT + caller_num
                send_sms(client, response_msg, contact, our_twilio_num, root_msg=last_msg_sent)  # IMPORTANT: we must set root_msg so that if they type HELPINFO in the middle of a conversation, we still don't lose track of where they are
            return HttpResponse('OK')

        matched_obj = re.match('back(.*)', msg_content, re.I|re.S)
        is_back_step = False
        if matched_obj and matched_obj.groups():
            is_back_step = True
            try:
                steps = int(matched_obj.group(1).strip())
            except: # 'back', 'back random 4', etc.
                steps = 1
            
            for step in range(steps):   # rewind
                option = MessageOption.objects.filter(child_msg=last_msg_sent).first()
                if option:
                    last_msg_sent = option.parent_msg
                else:
                    break

            sent_msgs = MessageRecord.objects.filter(message__isnull=False, task_queue=last_msg_record.task_queue, receiver_num=caller_num).order_by('-id')
            if sent_msgs.count() > steps:
                last_msg_record = sent_msgs[steps]
            else:
                last_msg_record = sent_msgs.last()

        # save msg first
        record = MessageRecord(content=msg_content, sender_num=caller_num, receiver_num=our_twilio_num, twilio_msg_sid=sms_sid, 
                           campaign=campaign, task_queue=task_queue, prompting_msg=last_msg_sent)
        record.save()


        if is_back_step:
            # send the msg, donot try to match the options
            response = last_msg_sent.get_full_content()
            send_sms(client, response, caller_num, our_twilio_num, campaign=campaign, task_queue=task_queue, root_msg=last_msg_sent)
        else:
            # helpinfo, HELPINFO, Helpinfo (we respond to them say "Here's the number for suicide prevention center: "; QUIT, quit, Quit (then we unsubscribe them from our message stream)
            # BACK, Back, back (will rewind the message to an earlier one)

            # Handle the end of the conversation
            if not last_msg_sent.options.exists():
                send_sms(client, THANKYOU, caller_num, our_twilio_num, campaign=campaign, task_queue=task_queue, root_msg=last_msg_sent)
                
            else:
                # checking if trigger keyword is nonexistent
                matched_msg_option = None
                user_response = msg_content.strip()

                for option in last_msg_sent.options.all():
                    trigger_keyword = option.trigger_keyword
                    # We will match "YEs" as well as "Yes!!" when researcher only definied "Yes" as keyword
                    # CAUTION: The first clause of checking if trigger != FREERESPONSE is important and must come first as a short-circuit
                    if (trigger_keyword != FREERESPONSE) and (re.match('^%s[^a-zA-Z0-9]*$'%trigger_keyword, user_response, re.I)):
                        matched_msg_option = option
                        break

                if not matched_msg_option:
                    for option in last_msg_sent.options.all():
                        if option.trigger_keyword == FREERESPONSE:
                            matched_msg_option = option
                            break

                # If we found a match in keyword, we respond
                if matched_msg_option:
                    # response here
                    response = matched_msg_option.child_msg.get_full_content()
                    send_sms(client, response, caller_num, our_twilio_num, campaign=campaign, task_queue=task_queue, root_msg=matched_msg_option.child_msg)
                else: # we tell them we don't understand
                    send_sms(client, DONT_UNDERSTAND, caller_num, our_twilio_num, campaign=campaign, task_queue=task_queue, root_msg=last_msg_sent)

        # need to know the last message they received
        return HttpResponse('OK')

class UserConversationView(LoginRequiredMixin, TemplateView):
    template_name = 'messages/view_conversation.html'
    
    def get_context_data(self, **kwargs):
        data = super(UserConversationView, self).get_context_data(**kwargs)
        phone_num = self.request.GET['username']
        if 'taskq_id' in self.request.GET:
            taskq_id = self.request.GET['taskq_id']
            taskq_obj = TaskQueue.objects.get(id=taskq_id)
            # messages replied/sent by student tied to a particular taskQ
            records = MessageRecord.objects.filter(task_queue=taskq_obj).filter(Q(receiver_num=phone_num)|Q(sender_num=phone_num))
        else: 
            records = MessageRecord.objects.filter(Q(receiver_num=phone_num)|Q(sender_num=phone_num))   # all messages sent/received by student

        data['records'] = records
        data['phone_number'] = phone_num
        return data

# TODO: unused. Check to make sure and remove
class ResponseFromStudentsByCampaignView(LoginRequiredMixin, TemplateView):
    template_name = 'messages/conversation_log.html'
    
    def get_context_data(self, **kwargs):
        data = super(ResponseFromStudentsByCampaignView, self).get_context_data(**kwargs)
        num = self.request.GET['num']        
        records = MessageRecord.objects.filter(Q(receiver_num=num)|Q(sender_num=num))
        data['records'] = records
        data['student_num'] = num
        return data

class TaskQueueConversationView(LoginRequiredMixin, TemplateView):
    template_name = 'messages/taskq_conversation.html'
    
    def get_context_data(self, **kwargs):
        data = super(TaskQueueConversationView, self).get_context_data(**kwargs)
        taskq_id = self.request.GET['taskq_id']
        taskq_obj = TaskQueue.objects.get(id=taskq_id)

        records = MessageRecord.objects.filter(task_queue=taskq_obj, message__isnull=True) # if 'message__isnull=True' then this is the message we received from students 
        data['records'] = records
        return data
