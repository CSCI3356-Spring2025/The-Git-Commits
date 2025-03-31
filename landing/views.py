from django.shortcuts import render, redirect
from django.views import View
from oauth.oauth import RequireLoggedInMixin
from django.http.response import HttpResponse
from landing.models import Assessment


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
        user = kwargs["user"]

        context = {"user_name": user.name, "user_role": user.role}
        return render(request, "landing/dashboard.html", context)

class StudentAssessmentView(RequireLoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        user = kwargs["user"]
        context = {
            'assessment_title': 'Peer Assessment 1',
            'due_date': 'Mar 20 @ 11:59PM ET',
            'user_name': user.name,
            'user_role': user.role
        }
        return render(request, 'landing/student_assessment.html', context)

    def post(self, request, *args, **kwargs):
        return redirect('landing:dashboard')

class NewStudentAssessmentView(RequireLoggedInMixin, View):
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

