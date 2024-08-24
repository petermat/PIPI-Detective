from django.db import models

from django.utils import timezone
#from django.conf import settings

#import logging
#logger = logging.getLogger(__name__)

from collector.models import Pipipackage

class Snapshot(models.Model):
    created = models.DateTimeField(default=timezone.now, blank=True)
    filename = models.CharField(max_length=2048)
    ruleset = models.JSONField(blank=True, null=True)
    findings = models.JSONField(blank=True, null=True)
    pipipackage = models.ForeignKey(Pipipackage, on_delete=models.CASCADE, related_name='snapshot')

    def __str__(self):
        return self.filename

