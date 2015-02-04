'''
Created on Feb 11, 2014

@author: lacheephyo
'''
DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '',    # database name
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',        # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',               # Set to empty string for default.
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# set another server t4s  = develop
# fo pre*.edu = master