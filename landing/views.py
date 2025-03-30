from django.shortcuts import render
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
    context = {
        'assessment_title': 'Peer Assessment 1',
        'due_date': 'March 31 @ 11:59pm ET',
    }
    return render(request, 'landing/student_assessment.html', context)
class DashboardView(RequireLoggedInMixin, View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user = kwargs["user"]

        context = {"user_name": user.name, "user_role": user.role}
        return render(request, "landing/dashboard.html", context)
