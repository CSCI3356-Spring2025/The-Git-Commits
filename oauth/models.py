from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser

class User(AbstractBaseUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]

    email = models.EmailField(unique=True, primary_key=True)
    name = models.CharField(max_length=120)
    role  = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def get_absolute_url(self) -> str:
        return f"/user/{self.id}/"

    def __str__(self):
        return self.name

    @property
    def is_admin(self):
        return self.role == 'admin'

    class Meta:
        ordering = ["role", "name"]
