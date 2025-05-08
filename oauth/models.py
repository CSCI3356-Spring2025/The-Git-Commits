from django.db import models
from django.db.models.fields.related import ForeignKey
from django.db.models.deletion import CASCADE
from landing.models import Course, Team
from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class AdminEmailAddress(models.Model):
    """Used to determine whether someone is an admin when they register their account"""
    email = models.EmailField(unique=True, primary_key=True, help_text="Email address of an admin or professor")
    
    def __str__(self) -> str:
        return self.email

class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]

    email = models.EmailField(unique=True, primary_key=True)
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    username = None  # Disable username field
    
    # Add default values for required fields
    password = models.CharField(max_length=128, default=uuid.uuid4().hex)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    # Add custom related names to avoid conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    courses = models.ManyToManyField('landing.Course', related_name="members", blank=True)
    teams = models.ManyToManyField('landing.Team', related_name="members", blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'role']
    
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
