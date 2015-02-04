'''
Created on Feb 28, 2014

@author: lacheephyo
'''
from django.core.cache import cache
from django.contrib import auth
from datetime import datetime
from django.conf import settings

class TimeOutCheckMiddleware(object):

    def process_request(self, request):
        user = request.user

        if user.is_authenticated():
            key = 'last_req_%s'%user.username
            last_time_logged = cache.get(key)
            if last_time_logged:
                time_elapsed = (datetime.now() - last_time_logged).seconds
                if time_elapsed > settings.LOGIN_TIME_OUT:
                    auth.logout(request)
                    
            cache.set(key, datetime.now())
