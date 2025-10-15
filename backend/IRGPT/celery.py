from celery import Celery
from decouple import config
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IRGPT.settings')

app = Celery('IRGPT')

app.config_from_object(
    'django.conf:settings', namespace='CELERY'
)
app.autodiscover_tasks()