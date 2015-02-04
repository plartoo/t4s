from django import forms
from accounts.models import Student
from organizations.models import Group, School
import re
from organizations.mixins import PhoneNumberFormMixin

class SchoolCreateForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ('name',)
        widgets = {
                'name': forms.TextInput(attrs={'size':'160'}),
        }

class StudentCreateForm(forms.ModelForm):
    phone_numbers = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Student
        exclude = ('user',)

        # if we want Django to check the phone number to make sure whether they contain alphabets
        #def clean_phone_numbers(self):

class GroupCreateForm(forms.ModelForm):
    name = forms.CharField(required=True, label='Group Name', widget=forms.TextInput(attrs={'size':'75'}))
    phone_numbers = forms.CharField(required=False, widget=forms.HiddenInput)
    class Meta:
        model = Group
        fields = ('name',)

class GroupNameEditForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name',)
        widgets = {
                'name': forms.TextInput(attrs={'size':'160'}),
        }

class GroupMembershipEditForm(forms.Form):
    phone_numbers = forms.CharField(required=False, widget=forms.HiddenInput)
    #school = forms.CharField(widget=forms.Select)

    """
    def __init__(self, *args, **kwargs):
        super(GroupMembershipEditForm, self).__init__(*args, **kwargs)
        schools = School.objects.all()
        choices = [(s.id, s.name) for s in schools]
        self.fields['school'].widget.choices = [['', '------'],] + choices
    """

class ContactEditForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ('contacts', 'help_reply',)
        placeholder_txt = "Type your customized reply for HELPINFO here."
        widgets = {
                'contacts': forms.Textarea(attrs={'cols': 180, 'rows': 3}),
                'help_reply': forms.Textarea(attrs={'cols': 180, 'rows': 3, 'placeholder': placeholder_txt}),
        }
        labels = {
            'contacts': 'Emergency contact numbers at this school:',
            'help_reply': 'Text we reply when student text us HELPINFO:'
        }        
        error_messages = {
            'help_reply': {
                'max_length': "SMS messages are limited to 160 characters.",
            },
        }

    def clean_contacts(self):
        data = self.data
        numbers = []
        for num in data['contacts'].split(','):
            # TODO: refactor this into PhoneNumberFormMixin
            phone_re = re.compile(r'^\d{10,15}$')
            if not phone_re.match(num.strip()):
                raise forms.ValidationError("Phone number(s): " + num + " must be numeric and between 10 to 15 digits long.")
            numbers.append(num.strip())

        return ','.join(numbers)

class SchoolAddStudentForm(PhoneNumberFormMixin, forms.Form):
    phone_numbers = forms.CharField(widget=forms.Textarea(attrs={'cols': 180, 'rows': 3}))
    role = forms.CharField(widget=forms.Select)

    def __init__(self, *args, **kwargs):
        super(SchoolAddStudentForm, self).__init__(*args, **kwargs)
        self.fields['phone_numbers'].label = 'Step 1: Add phone numbers [E.g., 5856261234,8613910912345]:'

        self.fields['role'].widget.choices = (('', '------'),) + Student.ROLE_CHOICES
        self.fields['role'].label = 'Step 2: Select roles of these phone numbers (if irrelevant, choose "Peer Leader"):'
        
class SchoolAddAdvisorForm(PhoneNumberFormMixin, forms.Form):
    phone_numbers = forms.CharField(widget=forms.Textarea(attrs={'cols': 180, 'rows': 3}))

    def __init__(self, *args, **kwargs):
        super(SchoolAddAdvisorForm, self).__init__(*args, **kwargs)
        self.fields['phone_numbers'].label = 'Add advisors (phone numbers):'
