'''
Created on Feb 12, 2014

@author: lacheephyo
'''
import re

from django import forms
from django.contrib import auth
from django.contrib.auth.models import User
from accounts.constants import STUDENT, ADVISOR, RESEARCHER
from django.core.cache import cache
from accounts.models import Student


class LoginForm(forms.Form):
    err_msg_1 = {'required': "Please enter phone number or user name.",
               'max_length': "The length of the characters should be no longer than 30."}
    err_msg_2 = {'required': "Please enter the password for your account."}
    
    username = forms.CharField(required=True, max_length=30, label="Phone Number", error_messages=err_msg_1)
    password = forms.CharField(required=True, widget=forms.PasswordInput(), error_messages=err_msg_2)

    def clean(self):
        data = self.data
        user = auth.authenticate(username=data['username'], password=data['password'])

        data = super(LoginForm, self).clean()

        if user:
            if not user.is_active:
                raise forms.ValidationError("Your registration isn't confirmed by us. Please contact text4strength.dev@gmail.com if you have completed registration and believe that you should have access to this website.")
            data['user'] = user
        else:
            raise forms.ValidationError('Invalid login: Phone Number and/or Password is incorrect.')
        
        return data

class RegisterForm(forms.Form):
    """
    some comment hre
    """
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=20)
    password2 = forms.CharField(max_length=20)

    phone = forms.CharField(required=False, max_length=11)
    email = forms.EmailField(required=False, max_length=100)
    firstname = forms.CharField(required=False, max_length=50)
    lastname = forms.CharField(required=False, max_length=50)
    verification_code = forms.CharField(required=False, max_length=10)
    school = forms.CharField(required=False)    # this is school ID (type Charfield) and will be used in Register View
    
    role = forms.CharField(max_length=20)

    def clean_password2(self):
        data = self.data
        if data.get('password') == data.get('password2'):
            return data['password']
        else:
            raise forms.ValidationError("Passwords didn't match")
        return data['password2']

    def clean_username(self):
        data = self.data
        if data.get('role') in [STUDENT, ADVISOR]:
            phone_re = re.compile(r'^1?\d{10,10}$')
            if not phone_re.match(data.get('username')):
                raise forms.ValidationError("Phone number must be numeric and between 10 to 11 digits long.")
        
        if User.objects.filter(username=data.get('username')):
            raise forms.ValidationError("User name (or phone number) has already been registered. Choose a different one if you're sure that you have not registered.")

        return data['username']

    def clean_email(self):
        data = self.data
        if data.get('role') in [RESEARCHER]:
            if not data.get('email'):
                raise forms.ValidationError("Email is required for researcher.")
            
        return data['email']
    
    def clean_verification_code(self):
        data = self.data
        if data.get('role') in [STUDENT, ADVISOR]:
            cached_verification_code = str( cache.get(data.get('username')) )
            if cached_verification_code != data.get('verification_code'):
                raise forms.ValidationError("Invalid verification code. Try again.")
        
        return data.get('verification_code')
    
    def clean_school(self):
        data = self.data
        if data.get('role') in [STUDENT, ADVISOR]:
            if not data.get('school'):
                raise forms.ValidationError("School is not registered in the database properly. Please contact the researcher.")
        return data.get('school')

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)
    new_password_repeat = forms.CharField(widget=forms.PasswordInput)


    def __init__(self, user, *args, **kwargs):      # this is to pass down 'user' to the form
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_new_password_repeat(self):
        data = self.data
        new_password = data.get('new_password')     # use 'get' in case they didn't provide anything 
        new_password_repeat = data.get('new_password_repeat')     # use 'get' in case they didn't provide anything

#         if not new_password or not new_password_repeat:   # must not be blank
#             raise forms.ValidationError("No password fields must be blank.")
        if (new_password != new_password_repeat):
            raise forms.ValidationError("New passwords didn't match. Please make sure they're the same.")
        
        return new_password_repeat

    def clean_old_password(self):
        data = self.data
        old_password = data.get('old_password')
        
#         if not old_password:
#             raise ("No password fields must be blank.")
        if not self.user.check_password(old_password):
            raise ("You must provide the correct password for 'old password' field.")

        return old_password

class UpdateProfileForm(forms.Form):
    conversation_limit_per_day = forms.IntegerField(min_value=0)
    
    def __init__(self, person, *args, **kwargs):    # to provide default value in the input form; requires us to create get_form() in the view
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.fields['conversation_limit_per_day'].initial = person.conversation_limit_per_day

class UpdateStudentProfileForm(UpdateProfileForm):
    role = forms.ChoiceField(Student.ROLE_CHOICES)
