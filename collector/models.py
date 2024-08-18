from django.db import models

from django.utils import timezone
#from django.conf import settings

#import logging
#logger = logging.getLogger(__name__)

class Pipipackage(models.Model):
    # on creation
    name = models.CharField(max_length=2048)
    summary = models.TextField(blank=True, null=True)
    version = models.CharField(max_length=2048, blank=True, null=True)
    python_versions = models.CharField(max_length=2048, blank=True, null=True)

    observed = models.DateTimeField(default=timezone.now, blank=True)
    created = models.DateTimeField(blank=True, null=True)
    logs_collected = models.DateTimeField(blank=True, null=True)

    top_rating = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_url(self):
        return f"https://pypi.org/project/{self.name}/"




