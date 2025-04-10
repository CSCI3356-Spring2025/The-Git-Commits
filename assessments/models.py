from django.db import models
from django.contrib import admin
import datetime

class Assessment(models.Model):
    title = models.CharField(max_length=150)
    due_date = models.DateTimeField(null=True)
    course = models.ForeignKey("landing.Course", models.CASCADE, related_name="assessments")
    published = models.BooleanField(default=False)

    def get_questions(self) -> models.QuerySet:
        return self.questions.all()

class AssessmentQuestion(models.Model):
    QUESTION_TYPES = [
        ('likert', 'Likert'),
        ('free', 'Free Response'),
    ]
    assessment = models.ForeignKey(Assessment, models.CASCADE, related_name="questions")
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    question = models.CharField(max_length=1000)
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]
