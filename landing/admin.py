from django.contrib import admin
from .models import Course, Team
from oauth.models import User

class ModelTeam(admin.ModelAdmin):
    list_display = ["name", "course_name"]

class TeamInline(admin.TabularInline):
    model = Team

class ModelCourse(admin.ModelAdmin):
    inlines = [TeamInline]
    list_display = ["name", "year", "semester"]


admin.site.register(Course, ModelCourse)
admin.site.register(Team, ModelTeam)
