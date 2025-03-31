from django.db import models
from django.contrib import admin
import datetime

class Course(models.Model):
    # Members are given by the foreign key on User, can be accessed with `courseObject.members`
    # Teams are given by the foreign key on User, can be accessed with `courseObject.teams`
    name = models.CharField(max_length=150, unique=True)
    year = models.IntegerField()
    semester = models.CharField(max_length=40)

    def __str__(self) -> str:
        return "{} ({} {})".format(self.name, self.year, self.semester)

    def get_members(self) -> models.QuerySet:
        return self.members.all()

    def get_team(self) -> models.QuerySet["Team"]:
        return self.teams.all()

    def get_assessments(self) -> models.QuerySet["Assessment"]:
        return self.assessments.all()

    def get_current_published_assessments(self) -> models.QuerySet["Assessment"]:
        return self.assessments.filter(due_date__gt=datetime.datetime.now(), published=True)

class Team(models.Model):
    # Members are given by the foreign key on User, can be accessed with `teamObject.members`
    name = models.CharField(max_length=150, unique=True)
    course = models.ForeignKey(Course, models.CASCADE, related_name="teams")

    def __str__(self) -> str:
        return self.name

    def get_members(self) -> models.QuerySet:
        return self.members.all()

    @admin.display(description="Course")
    def course_name(self) -> str:
        return self.course.name

    class Meta:
        ordering = ["course__name", "name"]


class Assessment(models.Model):
    title = models.CharField(max_length=150)
    due_date = models.DateTimeField()
    course = models.ForeignKey(Course, models.CASCADE, related_name="assessments")
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
