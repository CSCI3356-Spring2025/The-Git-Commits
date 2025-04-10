from django.contrib import admin
from .models import AssessmentQuestion, Assessment


class AssessmentQuestionInline(admin.TabularInline):
    model = AssessmentQuestion

class ModelAssessment(admin.ModelAdmin):
    inlines = [AssessmentQuestionInline]
    list_display = ["title", "due_date"]

admin.site.register(Assessment, ModelAssessment)
