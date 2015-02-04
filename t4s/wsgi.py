"""
WSGI config for t4s project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""
import os, sys

path = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(path, '..'))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "t4s.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
