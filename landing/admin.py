from django.contrib import admin
from .models import Course, Team, AssessmentQuestion, Assessment
from oauth.models import User

class ModelTeam(admin.ModelAdmin):
    list_display = ["name", "course_name"]

class TeamInline(admin.TabularInline):
    model = Team

class ModelCourse(admin.ModelAdmin):
    inlines = [TeamInline]
    list_display = ["name", "year", "semester"]


class AssessmentQuestionInline(admin.TabularInline):
    model = AssessmentQuestion

class ModelAssessment(admin.ModelAdmin):
    inlines = [AssessmentQuestionInline]
    list_display = ["title", "due_date"]

admin.site.register(Course, ModelCourse)
admin.site.register(Team, ModelTeam)
admin.site.register(Assessment, ModelAssessment)
