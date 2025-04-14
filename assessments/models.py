from django.db import models
from django.contrib import admin
from django.conf import settings
import datetime
from oauth.models import User

class Assessment(models.Model):
    title = models.CharField(max_length=150)
    due_date = models.DateTimeField(null=True)
    course = models.ForeignKey("landing.Course", models.CASCADE, related_name="assessments")
    published = models.BooleanField(default=False)
    allow_self_assessment = models.BooleanField(default=False)
    
    def get_questions(self) -> models.QuerySet:
        return self.questions.all()
    
    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)

        if is_new:
                # After saving a new assessment, automatically add the team member selection question
                team_question = AssessmentQuestion(
                    assessment=self,
                    question_type='team_member',
                    question='Who are you evaluating?',
                    required=True,
                    order=0  # Make 1st question
                )
                team_question.save()
                
                for question in self.questions.exclude(pk=team_question.pk):
                    question.order += 1                
                    question.save()

class AssessmentQuestion(models.Model):
    QUESTION_TYPES = [
        ('likert', 'Likert'),
        ('free', 'Free Response'),
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
