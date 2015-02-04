from datetime import datetime

from braces.views import LoginRequiredMixin, CsrfExemptMixin

from django.views.generic.edit import CreateView, FormView, UpdateView

from campaigns.models import Campaign, TaskQueue
from campaigns.forms import CampaignConversationForm, ConversationDuplicateForm,\
    SingleMessageConveresationCreateForm, MultipleMessageConveresationCreateForm,\
    ConversationTitleEditForm, ConversationSendForm

from django.core.urlresolvers import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView, RedirectView
from organizations.models import Group
from smsmessages.models import Message, MessageOption
from django.http.response import HttpResponse
import json
from django.contrib import messages
from campaigns.utils import copy_tree
from campaigns.mixins import ConversationMixin


# Researcher, Advisor, Member and Leaders will create campaigns
# 
# All Messages can be seen by Researcher
# Messages related to school will be seen by Advisor
# Messages related to composer (self) will be seen by composer (for Member and Leaders) 
# 
# Researcher and Adivsor will approve campaign
# 
# For now, we'll say
# User can see ALL messages he or she composed before
# 
# After user has created messages and tie them together under a campaign (say title "test campaign")
# When he logs in next time, what does he see when he clicks "Create Messages" for "test campaign"

# Create your views here.
class SingleMessageConversationCreateView(LoginRequiredMixin, ConversationMixin, CreateView):
    model = Campaign
    template_name = 'campaigns/messages/create_single_message.html'
    form_class = SingleMessageConveresationCreateForm

    def get_success_url(self):
        return reverse_lazy('campaigns:list')

    # when the form is valid, this method below will be called by CreateView
    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        data = form.cleaned_data
        
        msg = self.create_single_message(data)
        self.object = form.save(commit=False)
        self.object.composer = self.request.user
        self.object.root_message = msg
        self.object.update_search_keywords()  # for indexed search
        self.object.save()

        return super(SingleMessageConversationCreateView, self).form_valid(form)


class MultipleMessageConveresationCreateView(CsrfExemptMixin, LoginRequiredMixin, ConversationMixin, CreateView):
    model = Campaign
    template_name = 'campaigns/create_multiple_messages.html'
    form_class = MultipleMessageConveresationCreateForm
    success_url = reverse_lazy('campaigns:list')

    def get_context_data(self, **kwargs):
        data = super(MultipleMessageConveresationCreateView, self).get_context_data(**kwargs)
        if 'msg_id' in self.request.GET:
            cur_msg = Message.objects.get(id=self.request.GET['msg_id'])
            data['cur_msg'] = cur_msg
            
            # For "Back" button
            option = MessageOption.objects.filter(child_msg=cur_msg).first()
            if option:
                data['parent_msg'] = option.parent_msg

        if 'cam_id' in self.request.GET:
            campaign_obj = Campaign.objects.get(id=self.request.GET['cam_id'])
            data['campaign'] = campaign_obj
        data.update(self.request.GET.dict())    # this will add msg_id=1 & cam_id=1 to the context 
        return data

    # when the form is valid, this method below will be called by CreateView
    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        data = form.cleaned_data
        if self.request.GET.get('cam_id'):
            campaign_obj = Campaign.objects.get(id=self.request.GET['cam_id'])
        else:
            self.object = form.save(commit=False)
            self.object.composer = self.request.user
            self.object.save()
            campaign_obj = self.object

            
        if not self.request.GET.get('msg_id'):    # that means parent message has already been created before and we're just updating it, so don't create new obj
            # create parent msg here as root msg for cam
            cur_msg = Message()
            cur_msg.content = data['cur_msg']
            cur_msg.composer = self.request.user
            cur_msg.save()

            # set cam root msg
            campaign_obj.root_message = cur_msg
            campaign_obj.save()
            
        else:           # parent message did exist (meaning there's root msg already)
            cur_msg = Message.objects.get(id=self.request.GET['msg_id'])
            cur_msg.content = data['cur_msg']
            cur_msg.save()

        self.process_options(data['options'], cur_msg)
        campaign_obj.update_search_keywords()  # for indexed search
        
        messages.success(self.request, 'Message (update or creation) was successful')

        return HttpResponse(json.dumps({'result': 'success', 'cur_msg_id': cur_msg.id, 'cam_id': campaign_obj.id}))  # this is required because we are calling an AJAX to this function


class ConversationTitleEditView(LoginRequiredMixin, UpdateView):
    model = Campaign
    form_class = ConversationTitleEditForm
    template_name = 'campaigns/edit_conversation_title.html'
    success_url = reverse_lazy('campaigns:list')
    
    # when the form is valid, this method below will be called by CreateView
    def form_valid(self, form):
        result = super(ConversationTitleEditView, self).form_valid(form)
        # for indexed search. Here, this should come after super(...) is called 
        # so that form_valid(form) can update the object--the title--first before we call update_search_keywords
        self.object.update_search_keywords()  
        return result
    

class ConversationDuplicateView(LoginRequiredMixin, CreateView):
    model = Campaign
    template_name = 'campaigns/duplicate.html'
    form_class = ConversationDuplicateForm

    def get_form(self, form_class): # to pass down to Form Class so that user obj can be seen there
        campaign = Campaign.objects.get(id=self.request.GET['cam_id'])
        return form_class(campaign, **self.get_form_kwargs())

    def get_success_url(self):
        return '%s?cam_id=%s'%(reverse_lazy('campaigns:conversation_messages'), self.object.id)

    def get_context_data(self, **kwargs):
        data = super(ConversationDuplicateView, self).get_context_data(**kwargs)
        old_campaign = Campaign.objects.get(id=self.request.GET['cam_id'])
        data['old_campaign'] = old_campaign
        return data
    
    # when the form is valid, this method below will be called by CreateView
    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        self.object = form.save(commit=False)
        self.object.composer = self.request.user
        self.object.save()

        # copy the messages in the old camp.
        old_campaign = Campaign.objects.get(id=self.request.GET['cam_id'])
        # if msg_id exists, 
        if 'msg_id' in self.request.GET:
            msg_to_be_copied = Message.objects.get(id=self.request.GET['msg_id'])
            self.object.root_message = copy_tree(msg_to_be_copied, self.object.composer)
            self.object.save()
        else:
            if old_campaign.root_message:
                self.object.root_message = copy_tree(old_campaign.root_message, self.object.composer)
                self.object.save()
                
        self.object.update_search_keywords() # for indexed search

        return super(ConversationDuplicateView, self).form_valid(form)


class ConversationListView(LoginRequiredMixin, ListView):
    model = Campaign
    template_name = 'campaigns/list.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        data = super(ConversationListView, self).get_context_data(**kwargs)
        data.update(self.request.GET.items())
        data['order_field'] = data.get('order_field', 'created_at')
        data['order_by'] = data.get('order_by', '-')
        return data

    # queryset is needed below because we only want to list the ones composed just by the user (not by everyone)
    def get_queryset(self):
        qs = super(ConversationListView, self).get_queryset().exclude(status='deleted').filter(composer=self.request.user)
        search_keyword = self.request.GET.get('keywords')
        if search_keyword:
            # NOTE: added * after keyword to make sure search is complete when user entered keyword partially
            #qs = qs.filter(keywords__search='*' + search_keyword + '*') # this one doesn't work well in keywords like 'intro' for 'Test.Introduction'
            qs = qs.filter(keywords__icontains=search_keyword)

        qs = qs.order_by('-created_at')  # by default, show most recent
        # order the objects
        # check order_field and order_by in the request url
        order_field = self.request.GET.get('order_field')
        order_by = self.request.GET.get('order_by')
        if order_field:
            qs = qs.order_by('%s%s'%(order_by, order_field))
        return qs


class ConversationMessageTreeView(LoginRequiredMixin, TemplateView):
    model = Campaign
    template_name = 'campaigns/messages/tree_view.html'

    # the method below is to pass down parent_msg to template
    def get_context_data(self, **kwargs):
        data = super(ConversationMessageTreeView, self).get_context_data(**kwargs)
        cam = Campaign.objects.get(id=self.request.GET['cam_id'])
        data['campaign'] = cam
        return data


class ConversationSendView(LoginRequiredMixin, FormView):
    template_name = 'campaigns/send.html'
    form_class = ConversationSendForm
    success_url = reverse_lazy('campaigns:taskq_list')
    
    # the method below is to pass down parent_msg to template
    def get_context_data(self, **kwargs):
        data = super(ConversationSendView, self).get_context_data(**kwargs)
        data['groups'] = Group.objects.all()
        data['campaign'] = Campaign.objects.get(id=self.request.GET['cam_id'])
        return data

    def form_valid(self, form):
        """
        If the form is valid, save the associated model.
        """
        data = form.cleaned_data
        campaign_id = self.request.GET['cam_id']
        cam_obj = Campaign.objects.get(id=campaign_id)
        #groups = self.request.POST.getlist('selected_group_ids')
        groups = self.request.POST.getlist('selected_group_ids')[0].split(',')
        group_objs = Group.objects.in_bulk(groups).values()
        
        launch_time_str = data['launch_datetime']
        launch_time_obj = datetime.strptime(launch_time_str, '%Y-%m-%d %H:%M:%S')

        created_by_obj = self.request.user         
        #self.object.save() # this is not available in formview which does not require us to provide a "model" attribute


        task_queue = TaskQueue()
        task_queue.campaign = cam_obj
        task_queue.launch_time = launch_time_obj
        task_queue.created_by = created_by_obj
        # IMPORTANT: since taskq uses group as manytomany relation, 
        # we need to save this first to get taskq id which will be used in the campaigns_taskq_groups table
        task_queue.save() 

        task_queue.groups = group_objs

        return super(ConversationSendView, self).form_valid(form)


class TaskQueueListView(LoginRequiredMixin, ListView):
    model = TaskQueue
    template_name = 'campaigns/queue.html'
    paginate_by = 20

    # queryset is needed below because we only want to list the ones composed just by the user (not by everyone)
    # ListView will provide everything in the taskqueue
    def get_queryset(self):
        qs = super(TaskQueueListView, self).get_queryset().filter(created_by=self.request.user).exclude(status='deleted')
        
        if 'group' in self.request.GET:
            group_id = self.request.GET['group']
            if group_id != 'all-group':     # if user has NOT selected "All Groups" as filter
                group_obj = Group.objects.get(id=group_id)
                qs = qs.filter(groups=group_obj)
                
        if 'status' in self.request.GET:
            status = self.request.GET['status']
            
            if status != 'all-status': # if user has NOT selected "All Status" as filter
                qs = qs.filter(status=status)
        
        return qs.order_by('-id')

    def get_context_data(self, **kwargs):
        data = super(TaskQueueListView, self).get_context_data(**kwargs)
        data['groups'] = Group.objects.filter(created_by=self.request.user)
        data['statuses'] = TaskQueue.STATUS_CHOICES
        
        query_str = ''
        if 'group' in self.request.GET:
            group_id = self.request.GET['group']
            query_str += 'group=' + group_id + '&'

        if 'status' in self.request.GET:
            status = self.request.GET['status']
            query_str += 'status=' + status

        data['query_str'] = query_str

        data.update(self.request.GET.dict())        # passing argument like campaigns/queue/?group=4&status=sending back to the page
        
        return data

# TODO: This is for old conversatin/create page. I can remove this eventually including its template
class CampaignConversationCreateView(CsrfExemptMixin, LoginRequiredMixin, FormView):
    form_class = CampaignConversationForm
    template_name = 'campaigns/create_conversation.html'

    def get_success_url(self):
        return reverse_lazy('campaigns:conversation_messages') + '?cam_id=' + self.request.GET['cam_id'] 
    
    def get_context_data(self, **kwargs):
        data = super(CampaignConversationCreateView, self).get_context_data(**kwargs)
        if 'msg_id' in self.request.GET:
            parent_msg = Message.objects.get(id=self.request.GET['msg_id'])
            data['parent_msg'] = parent_msg
        data.update(self.request.GET.dict())    # this will add msg_id=1 & cam_id=1 to the context 
        return data

    def form_valid(self, form):
        data = form.cleaned_data
        campaign_obj = Campaign.objects.get(id=self.request.GET['cam_id'])
        if not self.request.GET.get('msg_id'):    # that means parent message has already been created before and we're just updating it, so don't create new obj
            # create parent msg here as root msg for cam
            parent_msg = Message()
            parent_msg.content = data['parent_msg_content']
            parent_msg.composer = self.request.user
            parent_msg.save()

            # set cam root msg
            campaign_obj.root_message = parent_msg
            campaign_obj.save()
            
        else:           # parent message did exist (meaning there's root msg already)
            parent_msg = Message.objects.get(id=self.request.GET['msg_id'])
            parent_msg.content = data['parent_msg_content']
            parent_msg.save()
                
            
        for option in data['options']:
            
            if 'option-id' in option:
                # update old option object
                option_obj = MessageOption.objects.get(id=option['option-id'])
                option_obj.child_msg.content = option['our-response']
                option_obj.child_msg.save()
                
                option_obj.trigger_keyword = option['keyword'].strip()  # case insensitive handling of keyword
                option_obj.option_content = option['option-text']
                #option_obj.separator = option['separator']
                #option_obj.respond_freely = option['freely-respond']
                option_obj.save()
                
            else:
                # create new option obj
                option_obj = MessageOption()
                
                child_msg = Message()
                child_msg.content = option['our-response']
                child_msg.composer = self.request.user
                child_msg.save()
                
                option_obj.child_msg = child_msg
                
                option_obj.trigger_keyword = option['keyword']
                option_obj.option_content = option['option-text']
                #option_obj.separator = option['separator']
                #option_obj.respond_freely = option.get('freely-respond', False) # this is because for newly created option object, the 'freely-respond' field is not returned by POST request
                option_obj.parent_msg = parent_msg
                option_obj.save()
        
        campaign_obj.update_search_keywords()
        messages.success(self.request, 'Message (update or creation) was successful')

        return HttpResponse(json.dumps({'result': 'success', 'parent_msg_id': parent_msg.id}))  # this is required because we are calling an AJAX to this function


class DeleteTaskQueueView(LoginRequiredMixin, RedirectView):
    permanent = False
    
    def get_redirect_url(self, *args, **kwargs):
        taskq_obj = TaskQueue.objects.get(id=self.request.GET['taskq_id'])
        taskq_obj.status = 'deleted'
        taskq_obj.save()
        return reverse_lazy('campaigns:taskq_list') + '?page=' + self.request.GET.get('page', '1')


class DeleteConversationView(LoginRequiredMixin, RedirectView):
    permanent = False
    
    def get_redirect_url(self, *args, **kwargs):
        taskq_obj = Campaign.objects.get(id=self.request.GET['cam_id'])
        taskq_obj.status = 'deleted'
        taskq_obj.save()
        return reverse_lazy('campaigns:list') #+ '?page=' + self.request.GET.get('page', '1')
