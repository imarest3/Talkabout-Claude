"""
WSGI config for talkabout project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'talkabout.settings')

application = get_wsgi_application()
