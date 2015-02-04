'''
Created on Feb 12, 2014

@author: lacheephyo
'''
from django import forms
from smsmessages.models import Message, MessageOption
from smsmessages.constants import FREERESPONSE
#from django.contrib import auth # Phyo: don't think we need this
#from django.contrib.auth.models import User # Phyo: don't think we need this


class MessageCreateForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content',)
        widgets = {
                'content': forms.Textarea(attrs={'cols': 80, 'rows': 5}),
        }
        error_messages = {
            'content': {
                'max_length': "SMS message is limited to 160 characters",
            },
        }


class MessageUpdateForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('content',)
        widgets = {
                'content': forms.Textarea(attrs={'cols': 80, 'rows': 5}),
        }
        error_messages = {
            'content': {
                'max_length': "SMS message is limited to 160 characters",
            },
        }

class AddOptionForm(forms.ModelForm):
    child_msg = forms.CharField(label='', widget=forms.TextInput(attrs={'type': 'hidden'}),
                                error_messages={'required': 'Please select from the child message that is already composed (shown by autocomplete).'})

    class Meta:
        model = MessageOption
        exclude = ('parent_msg',)
    def __init__(self, parent_msg, *args, **kwargs):
        super(AddOptionForm, self).__init__(*args, **kwargs)
        self.parent_msg = parent_msg
        # we need to call 'super' above before this self.fields is invoked
        # the reason is to make sure option_content can be nothing if trigger word is '*'
        self.fields['option_content'].required = False


    # this function is run before the form is validated
    def clean_child_msg(self):
        data = self.data    # it will return the value of child_msg form as a hash like {'child_msg': u'1'}
        return Message.objects.get(id=data['child_msg'])

    def clean_option_content(self):
        data = self.data


        if data['trigger_keyword'] != FREERESPONSE:
            if not data['option_content']:
                raise forms.ValidationError('Option content is required')
        return data['option_content']

    def clean_trigger_keyword(self):
        """
        Check if duplicate keyword has been entered
        .clean() # checking ALL form data
        clean_trigger_keyword() is called BEOFRE checking all form data
        Therefore, we don't want to call .clean() inside
        """
        data = self.cleaned_data
        if self.parent_msg.options.filter(trigger_keyword=data['trigger_keyword']).exists():
            raise forms.ValidationError('Trigger keyword has been chosen for this message. Choose another one')
        
        return data['trigger_keyword']
    