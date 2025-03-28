from django.contrib import admin
from .models import User, AdminEmailAddress

class ModelUser(admin.ModelAdmin):
    list_display = ["email", "name", "course_name", "role"]

admin.site.register(User, ModelUser)
admin.site.register(AdminEmailAddress)
