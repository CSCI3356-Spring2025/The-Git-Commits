from django.shortcuts import render, redirect
from django.views import View
from oauth.oauth import RequireLoggedInMixin
from django.http.response import HttpResponse


def landing_page(request):
    return render(request, 'landing/landing_page.html')

def dashboard(request):
    context = {
        'username': 'TestUser',
        'user_type': 'Professor',
    }
    return render(request, 'landing/dashboard.html', context)

def student_assessment_view(request):
    if request.method == 'POST':
        return redirect('landing:dashboard')
    
    context = {
        'assessment_title': 'Peer Assessment 1',
        'due_date': 'Mar 20 @ 11:59PM ET'
    }
    return render(request, 'landing/student_assessment.html', context)
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
