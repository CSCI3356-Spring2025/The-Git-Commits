from django.http.response import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.views import View
import datetime

from landing.models import Course, Team
from assessments.models import Assessment, AssessmentQuestion
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

class CreateTeamView(RequireAdminMixin, View):
    def get(self, request, *argv, **kwargs) -> HttpResponse:
        user: User = kwargs['user']
        if user.course is None:
            return redirect(reverse("landing:dashboard"))

        all_students = user.course.members.filter(role='student')
        available_students = user.course.members.filter(role='student', team__isnull=True) 

        editing_team_id = request.GET.get('edit_team')
        editing_team = None
        
        if editing_team_id:
            try:
                editing_team = Team.objects.get(pk=editing_team_id, course=user.course)
            except Team.DoesNotExist:
                pass
            
        context = {
            "teams": user.course.teams.all(),
            "course_name": user.course.name,
            "all_students": all_students,
            "available_students": available_students,
            "user": user,
            "editing_team": editing_team
        }
        return render(request, "landing/team_creation.html", context)
    
    def post(self, request, *argv, **kwargs) -> HttpResponse:
        user: User = kwargs['user']
        if user.course is None:
            return redirect(reverse("landing:dashboard"))

        action = request.POST.get('action', 'create_team')
        
        if action == 'create_team':
            return self._create_team(request, user)
        elif action == 'update_team':
            return self._update_team(request, user)
        elif action == 'delete_team':
            return self._delete_team(request, user)
        elif action == 'add_student':
            return self._add_student(request, user)
        elif action == 'create_course':
            return self._create_course(request, user)
        else:
            # Default to team creation if no valid action
            return self._create_team(request, user)
    
    def _create_team(self, request, user):
        """Handle team creation"""
        team_name = request.POST.get('name')
        member_emails = request.POST.getlist('member_emails', [])
        
        if not team_name:
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
        except Exception as e:
            all_students = user.course.members.filter(role='student')
            available_students = user.course.members.filter(role='student', team__isnull=True)
            
            context = {
                "teams": user.course.teams.all(),
                "course_name": user.course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "error": f"An error occurred: {str(e)}"
            }
            return render(request, 'landing/team_creation.html', context)
    
    def _update_team(self, request, user):
        """Handle updating an existing team"""
        team_id = request.POST.get('team_id')
        team_name = request.POST.get('team_name')
        member_emails = request.POST.getlist('member_emails', [])
        
        if not team_id or not team_name:
            all_students = user.course.members.filter(role='student')
            available_students = user.course.members.filter(role='student', team__isnull=True)
            
            context = {
                "teams": user.course.teams.all(),
                "course_name": user.course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "error": "Team ID and name are required"
            }
            return render(request, 'landing/team_creation.html', context)
        
        try:
            team = Team.objects.get(pk=team_id, course=user.course)
            
            team.name = team_name
            team.save()
            
            current_members = User.objects.filter(team=team)
            for member in current_members:
                member.team = None
                member.save()
            
            for email in member_emails:
                try:
                    member = User.objects.get(email=email)
                    if member.course == user.course:
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
                "success_message": f"Team '{team_name}' updated successfully!"
            }
            return render(request, 'landing/team_creation.html', context)
            
        except Team.DoesNotExist:
            all_students = user.course.members.filter(role='student')
            available_students = user.course.members.filter(role='student', team__isnull=True)
            
            context = {
                "teams": user.course.teams.all(),
                "course_name": user.course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "error": "Team not found"
            }
            return render(request, 'landing/team_creation.html', context)
    
    def _delete_team(self, request, user):
        """Handle team deletion"""
        team_id = request.POST.get('team_id')
        
        if not team_id:
            all_students = user.course.members.filter(role='student')
            available_students = user.course.members.filter(role='student', team__isnull=True)
            
            context = {
                "teams": user.course.teams.all(),
                "course_name": user.course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "error": "Team ID is required for deletion"
            }
            return render(request, 'landing/team_creation.html', context)
        
        try:
            team = Team.objects.get(pk=team_id, course=user.course)
            team_name = team.name

            current_members = User.objects.filter(team=team)
            for member in current_members:
                member.team = None
                member.save()
            
            team.delete()

            all_students = user.course.members.filter(role='student')
            available_students = user.course.members.filter(role='student', team__isnull=True)
            
            context = {
                "teams": user.course.teams.all(),
                "course_name": user.course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "success_message": f"Team '{team_name}' deleted successfully!"
            }
            return render(request, 'landing/team_creation.html', context)
            
        except Team.DoesNotExist:
            all_students = user.course.members.filter(role='student')
            available_students = user.course.members.filter(role='student', team__isnull=True)
            
            context = {
                "teams": user.course.teams.all(),
                "course_name": user.course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "error": "Team not found"
            }
            return render(request, 'landing/team_creation.html', context)
    
    def _add_student(self, request, user):
        """Handle adding a new student to the course"""
        student_name = request.POST.get('student_name')
        student_email = request.POST.get('student_email')
        
        if not student_name or not student_email:
            all_students = user.course.members.filter(role='student')
            available_students = user.course.members.filter(role='student', team__isnull=True)
            
            context = {
                "teams": user.course.teams.all(),
                "course_name": user.course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "error": "Student name and email are required"
            }
            return render(request, 'landing/team_creation.html', context)
        
        try:
            existing_student = User.objects.filter(email=student_email).first()
            
            if existing_student:
                if existing_student.course != user.course:
                    existing_student.course = user.course
                    existing_student.save()
                    success_message = f"Student '{student_name}' added to course!"
                else:
                    success_message = f"Student '{student_name}' is already in this course."
            else:
                new_student = User.objects.create(
                    name=student_name,
                    email=student_email,
                    role='student',
                    course=user.course
                )
                success_message = f"Student '{student_name}' created and added to course!"
            
            all_students = user.course.members.filter(role='student')
            available_students = user.course.members.filter(role='student', team__isnull=True)
            
            context = {
                "teams": user.course.teams.all(),
                "course_name": user.course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "success_message": success_message
            }
            return render(request, 'landing/team_creation.html', context)
            
        except Exception as e:
            all_students = user.course.members.filter(role='student')
            available_students = user.course.members.filter(role='student', team__isnull=True)
            
            context = {
                "teams": user.course.teams.all(),
                "course_name": user.course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "error": f"An error occurred: {str(e)}"
            }
            return render(request, 'landing/team_creation.html', context)
    
    def _create_course(self, request, user):
        """Handle creating a new course"""
        course_name = request.POST.get('course_name')
        course_year = request.POST.get('course_year')
        
        if not course_name or not course_year:
            all_students = user.course.members.filter(role='student') if user.course else []
            available_students = user.course.members.filter(role='student', team__isnull=True) if user.course else []
            
            context = {
                "teams": user.course.teams.all() if user.course else [],
                "course_name": user.course.name if user.course else "No Course",
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "error": "Course name and year are required"
            }
            return render(request, 'landing/team_creation.html', context)
        
        try:
            try:
                course_year = int(course_year)
            except ValueError:
                raise ValueError("Course year must be a number")
            
            new_course = create_new_course(course_name, course_year)
            
            user.course = new_course
            user.save()
            
            context = {
                "teams": new_course.teams.all(),
                "course_name": new_course.name,
                "all_students": [],
                "available_students": [],
                "user": user,
                "success_message": f"Course '{course_name}' created successfully!"
            }
            return render(request, 'landing/team_creation.html', context)
            
        except Exception as e:
            all_students = user.course.members.filter(role='student') if user.course else []
            available_students = user.course.members.filter(role='student', team__isnull=True) if user.course else []
            
            context = {
                "teams": user.course.teams.all() if user.course else [],
                "course_name": user.course.name if user.course else "No Course",
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "error": f"An error occurred: {str(e)}"
            }
            return render(request, 'landing/team_creation.html', context)


class CreateCourseView(RequireAdminMixin, View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs['user']
        context = {
            'user': user
        }
        return render(request, "landing/course_creation.html", context)
    
    def post(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs['user']
        course_name = request.POST.get('name')
        course_year = request.POST.get('year')
        
        if course_name and course_year:
            try:
                course_year = int(course_year)
                course = create_new_course(course_name, course_year)
                user.course = course 
                user.save()
                return redirect(reverse("landing:team_creation"))
            except ValueError:
                return render(request, 'landing/course_creation.html',
                            {'error': 'Invalid year'})
        
        return render(request, 'landing/course_creation.html',
                     {'error': 'Course name and year required'})
    
def add_team_redirect(request, *argv, **kwargs):
    context = {'course': 'Software Engineering',
               'team': 'The Git Commits'}

    return render(request, 'landing/team_creation.html')

class CourseListView(RequireAdminMixin, View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]

        context = {
            "user_name": user.name,
            "user_role": user.role,
            "user_team": user.team.name if user.team else "",
            "courses": Course.objects.all() 
        }
        
        return render(request, "landing/course_list.html", context)
