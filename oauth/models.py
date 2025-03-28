from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE
from landing.models import Course, Team
from django.contrib import admin

class AdminEmailAddress(models.Model):
    """Used to determine whether someone is an admin when they register their account"""
    email = models.EmailField(unique=True, primary_key=True, help_text="Email address of an admin or professor")
    
    def __str__(self) -> str:
        return self.email

class User(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]

    email = models.EmailField(unique=True, primary_key=True)
    name = models.CharField(max_length=120)
    role  = models.CharField(max_length=10, choices=ROLE_CHOICES)

    course = models.ForeignKey(Course, models.SET_NULL, related_name="members", null=True)
    team = models.ForeignKey(Team, models.SET_NULL, related_name="members", null=True)

    def get_absolute_url(self) -> str:
        return f"/user/{self.email}/"

    def __str__(self) -> str:
        return self.name

    def is_admin(self) -> bool:
        return self.role == 'admin'

    @admin.display(description="Course")
    def course_name(self) -> str:
        if self.course:
            return self.course.name
        else:
            return "No course"

    class Meta:
        ordering = ["role", "name"]
