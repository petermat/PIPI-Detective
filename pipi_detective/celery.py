import os

from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pipi_detective.settings')

app = Celery(
    'pipi_detective',
    broker='redis://%s:%d/%d' % (settings.REDIS_HOST, settings.REDIS_PORT,
        settings.REDIS_DB),
    backend='redis://%s:%d/%d' % (settings.REDIS_HOST, settings.REDIS_PORT,
        settings.REDIS_DB)
    )


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
#app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')