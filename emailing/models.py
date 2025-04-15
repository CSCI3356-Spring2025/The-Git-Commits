from django.db import models
from assessments.models import Assessment
from django.db.models.deletion import CASCADE

class EmailRecord(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=CASCADE, related_name="email_records")
    almost_due_sent = models.BooleanField()
    publish_sent = models.BooleanField()
