from django.db import models
from django.contrib import admin

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


