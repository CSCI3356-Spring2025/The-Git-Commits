from django.db import models
from django.contrib import admin
from django.conf import settings
import datetime
from oauth.models import User
from django.utils import timezone

class Assessment(models.Model):
    title = models.CharField(max_length=150)
    due_date = models.DateTimeField(null=True)
    publish_date = models.DateTimeField(null=True)
    course = models.ForeignKey("landing.Course", models.CASCADE, related_name="assessments")
    allow_self_assessment = models.BooleanField(default=False)

    publish_email_sent = models.BooleanField(default=False)
    due_soon_email_sent = models.BooleanField(default=False)
    
    def get_questions(self) -> models.QuerySet:
        return self.questions.all()
    
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
    
    def is_current(self) -> bool:
        if not (self.due_date and self.publish_date):
            return False
        time_now = timezone.now()
        return (time_now <= self.due_date) and (time_now >= self.publish_date)

class AssessmentQuestion(models.Model):
    QUESTION_TYPES = [
        ('likert', 'Likert'),
        ('free', 'Free Response'),

        # I really don't think we should have this. There must be exactly one in every assessment, so
        # storing it like other questions is just another thing that can break, and must be
        # handled completely differently from the other questions, creating unnecessary edge cases
        ('team_member', 'Team Member Selection')
    ]
    assessment = models.ForeignKey(Assessment, models.CASCADE, related_name="questions")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    question = models.CharField(max_length=1000)
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]

class StudentAssessmentResponse(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    evaluated_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="evaluations_received", null=True, blank=True)

class StudentAnswer(models.Model):
    response = models.ForeignKey(StudentAssessmentResponse, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(AssessmentQuestion, on_delete=models.CASCADE)
    # We'll need to handle the difference between free response and Likert
    answer_text = models.TextField(blank=True, null=True)
