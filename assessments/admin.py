from django.contrib import admin
from .models import AssessmentQuestion, Assessment, StudentAnswer, StudentAssessmentResponse


class AssessmentQuestionInline(admin.TabularInline):
    model = AssessmentQuestion

class ModelAssessment(admin.ModelAdmin):
    inlines = [AssessmentQuestionInline]
    list_display = ["title", "due_date"]


class AnswerInline(admin.TabularInline):
    model = StudentAnswer

class ModelStudentAssessmentResponse(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ["student", "evaluated_user", "assessment"]

admin.site.register(Assessment, ModelAssessment)
admin.site.register(StudentAssessmentResponse, ModelStudentAssessmentResponse)
