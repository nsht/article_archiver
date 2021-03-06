import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'article_archiver.settings')

app = Celery('article_archiver')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()