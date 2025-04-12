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

    courses = models.ManyToManyField('landing.Course', related_name="members", blank=True)
    teams = models.ManyToManyField('landing.Team', related_name="members", blank=True)
    
    def get_absolute_url(self) -> str:
        return f"/user/{self.email}/"

    def __str__(self) -> str:
        return self.name

    def is_admin(self) -> bool:
        return self.role == 'admin'

    @admin.display(description="Course")
    def course_name(self) -> str:
        courses = self.courses.all()  # Fetch all courses the user is enrolled in
        if courses.exists():
            return ", ".join([course.name for course in courses])  # Join course names as a string
        else:
            return "No courses"

    class Meta:
        ordering = ["role", "name"]
