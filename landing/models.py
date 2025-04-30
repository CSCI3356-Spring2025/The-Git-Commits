from django.db import models
from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import User
import datetime

class Course(models.Model):
    name = models.CharField(max_length=150, unique=True)
    year = models.IntegerField()
    semester = models.CharField(max_length=40)

    def __str__(self) -> str:
        return "{} ({} {})".format(self.name, self.year, self.semester)

    def get_members(self) -> models.QuerySet:
        return self.members.all()

    def get_teams(self) -> models.QuerySet["Team"]:
        return self.teams.all()

    def get_assessments(self) -> models.QuerySet["assessments.Assessment"]:
        return self.assessments.all()

    def get_current_published_assessments(self) -> models.QuerySet["assessments.Assessment"]:
        time_now = datetime.datetime.now()
        return self.assessments.exclude(due_date__gt=time_now).filter(publish_date__lt=time_now)

class Team(models.Model):
    # Members can be accessed with `team.members.all()`
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

