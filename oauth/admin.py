from django.contrib import admin
from .models import User, AdminEmailAddress

admin.site.register(User)
admin.site.register(AdminEmailAddress)
