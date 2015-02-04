'''
Created on Feb 12, 2014

@author: lacheephyo
'''
from django import forms
from campaigns.models import Campaign
import json

class SingleMessageConveresationCreateForm(forms.ModelForm):
    err_msgs = {'required': "You must type in the content of the message.", 
               'max_length': "The message length should be no longer than the limit below."}
    parent_msg = forms.CharField(max_length=160, error_messages=err_msgs)
    reply_msg = forms.CharField(max_length=160, error_messages=err_msgs)

    class Meta:
        model = Campaign
        fields = ('title',)
        error_messages = {
            'title': {
                'required': "The title of the conversation is required.",
            }
        }


class MultipleMessageConveresationCreateForm(forms.ModelForm):
    cur_msg = forms.CharField(max_length=160)
    options = forms.CharField() # these two vars should be the same name as AJAX dict keys

    class Meta:
        model = Campaign
        fields = ('title',)

    def clean_options(self):
        data = self.data
        options = json.loads(data['options'])
        return options  # this will go to form_valid of CampaignCreateConversationView


class ConversationTitleEditForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ('title',)
        widgets = {
                'title': forms.TextInput(attrs={'size':'160'}),
        }


class ConversationSendForm(forms.Form):
    datetime_err_msgs = {'required': "You must select a time to send this conversation."}
    group_err_msgs = {'required': "You must select at least one group to send this conversation."}
    
    launch_datetime = forms.CharField(required=True, error_messages=datetime_err_msgs)
    #selected_group_ids = forms.CharField(required=True, error_messages=group_err_msgs)
    selected_group_ids = forms.CharField(required=True, error_messages=group_err_msgs, widget=forms.HiddenInput)

class CampaignConversationForm(forms.Form):
    options = forms.CharField() # these two vars should be the same name as AJAX dict keys
    parent_msg_content = forms.CharField(required=False)    # Once we've created it, we don't require it to exist

    def clean_options(self):
        data = self.data
        options = json.loads(data['options'])
        return options  # this will go to form_valid of CampaignCreateConversationView


class ConversationDuplicateForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ('title',)
        widgets = {
                'title': forms.TextInput(attrs={'size':'160'}),
        }

    def __init__(self, campaign, *args, **kwargs):      # this is to get 'campaign' object from CampaignDuplicateView via get_form() 
        super(ConversationDuplicateForm, self).__init__(*args, **kwargs)
        self.fields['title'].initial = 'Copy of ' + campaign.title # to set default for title 
