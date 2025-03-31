from django.shortcuts import render, redirect
from django.views import View
from oauth.oauth import RequireLoggedInMixin
from django.http.response import HttpResponse
from landing.models import Assessment
from oauth.models import User
from django.db.models.query import QuerySet


def landing_page(request):
    return render(request, 'landing/landing_page.html')

def dashboard(request):
    context = {
        'username': 'TestUser',
        'user_type': 'Professor',
    }
    return render(request, 'landing/dashboard.html', context)

class DashboardView(RequireLoggedInMixin, View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        if user.course:
            assessments = user.course.get_current_published_assessments()
        else:
            assessments = Assessment.objects.none()

        context = {
            "user_name": user.name,
            "user_role": user.role,
            "assessments": assessments
        }
        return render(request, "landing/dashboard.html", context)

class StudentAssessmentView(RequireLoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        user = kwargs["user"]
        assessment_id = kwargs["assessment_id"]
        try:
            assessment = Assessment.objects.get(pk=assessment_id)
        except Assessment.DoesNotExist:
            return redirect(reverse("dashboard"))

        # TODO: check that the user is in the course the assessment is intended for

        context = {
            'assessment_title': assessment.title,
            'due_date': assessment.due_date,
            'questions': assessment.get_questions(),
            'user_name': user.name,
            'user_role': user.role
        }
        return render(request, 'landing/new_student_assessment.html', context)

    def post(self, request, *args, **kwargs):
        return redirect('landing:dashboard')

class StudentAssessmentListView(RequireLoggedInMixin, View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        if user.course:
            assessments = user.course.get_current_published_assessments()
        else:
            assessments = Assessment.objects.none()

        context = {
            "user_name": user.name,
            "user_role": user.role,
            "assessments": assessments
        }
        return render(request, "landing/student_assessment_list.html", context)
