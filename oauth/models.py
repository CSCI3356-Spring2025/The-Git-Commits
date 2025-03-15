from django.db import models

# Create your models here.
class User(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]

    name  = models.CharField(max_length=120)
    user_class = models.CharField(max_length=50)  # 'class' is a reserved keyword, renamed to 'user_class'
    email = models.EmailField(unique=True)
    role  = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def get_absolute_url(self):
        return f"/user/{self.id}/"