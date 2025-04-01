from django.http.response import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.views import View
import datetime

from landing.models import Course, Assessment, AssessmentQuestion, Team
from oauth.models import User
from django.db.models.query import QuerySet
from landing.courses import create_new_team, create_new_course
from oauth.oauth import RequireLoggedInMixin, RequireAdminMixin


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
            course_name = user.course.name
            assessments = user.course.get_current_published_assessments()
        else:
            course_name = "You're not registered with a class"
            assessments = Assessment.objects.none()

        context = {
            "user_name": user.name,
            "user_role": user.role,
            "course_name": course_name,
            "assessments": assessments
        }
        if user.role == "admin":
            return render(request, "landing/professor_dashboard.html", context)
        else:
            return render(request, "landing/student_dashboard.html", context)

class StudentAssessmentView(RequireLoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        user = kwargs["user"]
        assessment_id = kwargs["assessment_id"]
        try:
            assessment = Assessment.objects.get(pk=assessment_id)
        except Assessment.DoesNotExist:
            return redirect(reverse("dashboard"))

        # TODO: check that the user is in the course the assessment is intended for
        if user.course != assessment.course:
            return redirect(reverse("landing:dashboard"))

        context = {
            'assessment_title': assessment.title,
            'due_date': assessment.due_date,
            'questions': assessment.get_questions(),
            'user_name': user.name,
            'user_role': user.role
        }
        return render(request, 'landing/new_student_assessment.html', context)

    def post(self, request, *args, **kwargs):
        return redirect('landing:student_assessment_list')

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
    def post(self, request, *args, **kwargs):
        #TODO: We can process the data from the form here later
        return redirect(reverse('landing:student_assessment_list'))

class CreateTeamView(RequireAdminMixin, View):
    def get(self, request, *argv, **kwargs) -> HttpResponse:
        user: User = kwargs['user']
        if user.course is None:
            return redirect(reverse("landing:dashboard"))

        all_students = user.course.members.filter(role='student')
        available_students = user.course.members.filter(role='student', team__isnull=True) 

        context = {
            "teams": user.course.teams.all(),
            "course_name": user.course.name,
            "all_students": all_students,
            "available_students": available_students,
            "user": user
        }
        return render(request, "landing/team_creation.html", context)
    
    def post(self, request, *argv, **kwargs) -> HttpResponse:
        user: User = kwargs['user']
        if user.course is None:
            return redirect(reverse("landing:dashboard"))

        team_name = request.POST.get('name')
        member_emails = request.POST.getlist('member_emails', [])
        
        if team_name:
            try:
                team = create_new_team(team_name, user.course.name)
                
                for email in member_emails:
                    try:
                        member = User.objects.get(email=email)
                        if member.course == user.course:
                            if member.team:
                                member.team = None
                                member.save()
                            
                            member.team = team
                            member.save()
                    except User.DoesNotExist:
                        continue

                all_students = user.course.members.filter(role='student')
                available_students = user.course.members.filter(role='student', team__isnull=True)
                
                context = {
                    "teams": user.course.teams.all(),
                    "course_name": user.course.name,
                    "all_students": all_students,
                    "available_students": available_students,
                    "user": user,
                    "success_message": f"Team '{team_name}' created successfully!"
                }
                return render(request, 'landing/team_creation.html', context)
                
            except Course.DoesNotExist:
                all_students = user.course.members.filter(role='student')
                available_students = user.course.members.filter(role='student', team__isnull=True)
                
                context = {
                    "teams": user.course.teams.all(),
                    "course_name": user.course.name,
                    "all_students": all_students,
                    "available_students": available_students,
                    "user": user,
                    "error": "Course not found"
                }
                return render(request, 'landing/team_creation.html', context)

        all_students = user.course.members.filter(role='student')
        available_students = user.course.members.filter(role='student', team__isnull=True)
        
        context = {
            "teams": user.course.teams.all(),
            "course_name": user.course.name,
            "all_students": all_students,
            "available_students": available_students,
            "user": user,
            "error": "Team name is required"
        }
        return render(request, 'landing/team_creation.html', context)

class CreateCourseView(RequireAdminMixin, View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        context = {}
        return render(request, "landing/course_creation.html", context)
    
    def post(self, request, *args, **kwargs) -> HttpResponse:
        course_name = request.POST.get('name')
        course_year = request.POST.get('year')
        
        if course_name and course_year:
            try:
                course_year = int(course_year)
                course = create_new_course(course_name, course_year)
                return redirect(reverse("landing:dashboard"))
            except ValueError:
                return render(request, 'landing/course_creation.html',
                            {'error': 'Invalid year'})
        
        return render(request, 'landing/course_creation.html',
                     {'error': 'Course name and year required'})

class CreateAssessmentView(RequireAdminMixin, View):
    # Right now we're assuming this will create a new assessment, not edit an existing one
    def get(self, request, *argv, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        if user.course is None:
            return redirect(reverse("landing:dashboard"))

        # Determine which assessment this is for (creating a new one if necessary)
        assessment_id = request.session.get("assessment_id", None)
        if assessment_id: 
            assessment = Assessment.objects.get(pk=assessment_id)
        else:
            assessment = Assessment.objects.create(course = user.course, title="New Assessment", due_date=None, published=False)
            request.session["assessment_id"] = assessment.pk

        context = {"assessment": assessment}
        return render(request, "landing/assessment_creation.html", context)

    def post(self, request, *argv, **kwargs) -> HttpResponse:
        """Buttons that have to update the page send POST requests back to update the database
        and re-render the page. Doing it this way instead of using basic JS feels like a war crime,
        but the requirements make it necessary.
        """
        user: User = kwargs["user"]
        if user.course is None:
            return redirect(reverse("landing:dashboard"))

        # Determine which assessment this is for
        assessment_id = request.session.get("assessment_id", None)
        if assessment_id: 
            assessment = Assessment.objects.get(pk=assessment_id)
        else:
            assessment = Assessment.objects.create(
                course = user.course,
                title="New Assessment",
                # Default to tomorrow for now
                due_date=datetime.datetime.now() + datetime.timedelta(days=1),
                published=False
            )
            request.session["assessment_id"] = assessment.pk

        # Process the incoming action from the request data
        # TODO: factor this out into another function
        params = request.POST
        if params.get("add", None):
            question = AssessmentQuestion.objects.create(assessment=assessment, question_type="likert", question="Question text?", required=True)

        elif params.get("remove", None):
            pk = params["remove"]
            AssessmentQuestion.objects.filter(pk=pk).delete()

        elif params.get("edit", None):
            pk = params["edit"]
            question = AssessmentQuestion.objects.get(pk=pk)

            required = params.get("required", None)
            question_text = params.get("question", None)
            question_type = params.get("question_type", None)
            if required is not None:
                question.required = (required == "on")
            if question_text is not None:
                question.question = question_text
            if question_type == "likert" or question_type == "free":
                question.question_type = question_type

            question.save()

        elif params.get("publish", None):
            assessment.published = True
            assessment.save()
            del request.session["assessment_id"]
            request.session.modified = True
            return redirect("landing:dashboard")


        context = { "assessment": assessment }
        return render(request, "landing/assessment_creation.html", context)
    
def add_team_redirect(request, *argv, **kwargs):
    context = {'course': 'Software Engineering',
               'team': 'The Git Commits'}

    return render(request, 'landing/team_creation.html')


