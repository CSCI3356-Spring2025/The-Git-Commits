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
        if user.courses.exists():  # Check if the user is enrolled in any course
            course = user.courses.first()  # Get the first course for now, or handle it differently if needed
            course_name = course.name
            assessments = course.get_current_published_assessments()
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
        course_id = request.GET.get('course_id')
        
        # If course_id provided, fetch that specific course
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
                # Verify admin has access to this course
                if user.role != 'admin':
                    return redirect(reverse("landing:dashboard"))
            except Course.DoesNotExist:
                return redirect(reverse("landing:course_list"))
        else:
            # Fallback to user's default course
            if not user.courses.exists():
                return redirect(reverse("landing:dashboard"))
            course = user.courses.first()

        # Get students for this specific course
        all_students = course.members.filter(role='student')
        available_students = course.members.filter(role='student', teams__isnull=True) 

        editing_team_id = request.GET.get('edit_team')
        editing_team = None
        
        if editing_team_id:
            try:
                editing_team = Team.objects.get(pk=editing_team_id, course=course)
            except Team.DoesNotExist:
                pass
            
        context = {
            "teams": course.teams.all(),
            "course": course,  # Add the course object
            "course_name": course.name,
            "all_students": all_students,
            "available_students": available_students,
            "user": user,
            "user_name": user.name,  # Add these for navbar consistency
            "user_role": user.role,
            "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

            "editing_team": editing_team
        }
        return render(request, "landing/team_creation.html", context)
    
    def post(self, request, *argv, **kwargs) -> HttpResponse:
        user: User = kwargs['user']
        course_id = request.POST.get('course_id')
        
        # Determine which course we're working with
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
                if user.role != 'admin':
                    return redirect(reverse("landing:dashboard"))
            except Course.DoesNotExist:
                if not user.courses.exists():
                    return redirect(reverse("landing:dashboard"))
                course = user.courses.first()
        else:
            if not user.courses.exists():
                return redirect(reverse("landing:dashboard"))
            course = user.courses.first()

        action = request.POST.get('action', 'create_team')
        
        # Pass the course to the appropriate action method
        if action == 'create_team':
            return self._create_team(request, user, course)
        elif action == 'update_team':
            return self._update_team(request, user, course)
        elif action == 'delete_team':
            return self._delete_team(request, user, course)
        elif action == 'add_student':
            return self._add_student(request, user, course)
        else:
            # Default to team creation if no valid action
            return self._create_team(request, user, course)
    
    def _create_team(self, request, user, course):
        """Handle team creation"""
        team_name = request.POST.get('name')
        member_emails = request.POST.getlist('member_emails', [])
        
        if not team_name:
            all_students = course.members.filter(role='student')
            available_students = course.members.filter(role='student', teams__isnull=True)
            
            context = {
                "teams": course.teams.all(),
                "course": course,
                "course_name": course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "user_name": user.name,
                "user_role": user.role,
                "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

                "error": "Team name is required"
            }
            return render(request, 'landing/team_creation.html', context)
        
        try:
            team = create_new_team(team_name, course.name)
            
            for email in member_emails:
                try:
                    member = User.objects.get(email=email)
                    if course in member.courses.all():
                        if member.team:
                            member.team = None
                            member.save()
        
                        member.teams.add(team)
                except User.DoesNotExist:
                    continue
            
            all_students = course.members.filter(role='student')
            available_students = course.members.filter(role='student', teams__isnull=True)
            
            context = {
                "teams": course.teams.all(),
                "course": course,
                "course_name": course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "user_name": user.name,
                "user_role": user.role,
                "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

                "success_message": f"Team '{team_name}' created successfully!"
            }
            return render(request, 'landing/team_creation.html', context)
            
        except Course.DoesNotExist:
            all_students = course.members.filter(role='student')
            available_students = course.members.filter(role='student', teams__isnull=True)
            
            context = {
                "teams": course.teams.all(),
                "course": course,
                "course_name": course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "user_name": user.name,
                "user_role": user.role,
                "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

                "error": "Course not found"
            }
            return render(request, 'landing/team_creation.html', context)
        except Exception as e:
            all_students = course.members.filter(role='student')
            available_students = course.members.filter(role='student', teams__isnull=True)
            
            context = {
                "teams": course.teams.all(),
                "course": course,
                "course_name": course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "user_name": user.name,
                "user_role": user.role,
                "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

                "error": f"An error occurred: {str(e)}"
            }
            return render(request, 'landing/team_creation.html', context)
    
    def _update_team(self, request, user, course):
        """Handle updating an existing team"""
        team_id = request.POST.get('team_id')
        team_name = request.POST.get('team_name')
        member_emails = request.POST.getlist('member_emails', [])
        
        if not team_id or not team_name:
            all_students = course.members.filter(role='student')
            available_students = course.members.filter(role='student', teams__isnull=True)
            
            context = {
                "teams": course.teams.all(),
                "course": course,
                "course_name": course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "user_name": user.name,
                "user_role": user.role,
                "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

                "error": "Team ID and name are required"
            }
            return render(request, 'landing/team_creation.html', context)
        
        try:
            team = Team.objects.get(pk=team_id, course=course)
            
            team.name = team_name
            team.save()
            
            current_members = team.members.all()
            for member in current_members:
                team.members.clear()
            
            for email in member_emails:
                try:
                    member = User.objects.get(email=email)
                    if course in member.courses.all():
                        team.members.clear()
                except User.DoesNotExist:
                    continue
        
            all_students = course.members.filter(role='student')
            available_students = course.members.filter(role='student', teams__isnull=True)
            
            context = {
                "teams": course.teams.all(),
                "course": course,
                "course_name": course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "user_name": user.name,
                "user_role": user.role,
                "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

                "success_message": f"Team '{team_name}' updated successfully!"
            }
            return render(request, 'landing/team_creation.html', context)
            
        except Team.DoesNotExist:
            all_students = course.members.filter(role='student')
            available_students = course.members.filter(role='student', teams__isnull=True)
            
            context = {
                "teams": course.teams.all(),
                "course": course,
                "course_name": course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "user_name": user.name,
                "user_role": user.role,
                "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

                "error": "Team not found"
            }
            return render(request, 'landing/team_creation.html', context)
    
    def _delete_team(self, request, user, course):
        """Handle team deletion"""
        team_id = request.POST.get('team_id')
        
        if not team_id:
            all_students = course.members.filter(role='student')
            available_students = course.members.filter(role='student', teams__isnull=True)
            
            context = {
                "teams": course.teams.all(),
                "course": course,
                "course_name": course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "user_name": user.name,
                "user_role": user.role,
                "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

                "error": "Team ID is required for deletion"
            }
            return render(request, 'landing/team_creation.html', context)
        
        try:
            team = Team.objects.get(pk=team_id, course=course)
            team_name = team.name

            current_members = User.objects.filter(team=team)
            for member in current_members:
                team.members.clear()
            
            team.delete()

            all_students = course.members.filter(role='student')
            available_students = course.members.filter(role='student', teams__isnull=True)
            
            context = {
                "teams": course.teams.all(),
                "course": course,
                "course_name": course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "user_name": user.name,
                "user_role": user.role,
                "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

                "success_message": f"Team '{team_name}' deleted successfully!"
            }
            return render(request, 'landing/team_creation.html', context)
            
        except Team.DoesNotExist:
            all_students = course.members.filter(role='student')
            available_students = course.members.filter(role='student', teams__isnull=True)
            
            context = {
                "teams": course.teams.all(),
                "course": course,
                "course_name": course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "user_name": user.name,
                "user_role": user.role,
                "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

                "error": "Team not found"
            }
            return render(request, 'landing/team_creation.html', context)
    
    def _add_student(self, request, user, course):
        """Handle adding a new student to the course"""
        student_name = request.POST.get('student_name')
        student_email = request.POST.get('student_email')
        
        if not student_name or not student_email:
            all_students = course.members.filter(role='student')
            available_students = course.members.filter(role='student', teams__isnull=True)
            
            context = {
                "teams": course.teams.all(),
                "course": course,
                "course_name": course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "user_name": user.name,
                "user_role": user.role,
                "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

                "error": "Student name and email are required"
            }
            return render(request, 'landing/team_creation.html', context)
        
        try:
            existing_student = User.objects.filter(email=student_email).first()
            
            if existing_student:
                if existing_student.course != course:
                    existing_student.course = course
                    existing_student.save()
                    success_message = f"Student '{student_name}' added to course!"
                else:
                    success_message = f"Student '{student_name}' is already in this course."
            else:
                new_student = User.objects.create(
                    name=student_name,
                    email=student_email,
                    role='student',
                )
                new_student.courses.add(course)
                success_message = f"Student '{student_name}' created and added to course!"
            
            all_students = course.members.filter(role='student')
            available_students = course.members.filter(role='student', teams__isnull=True)
            
            context = {
                "teams": course.teams.all(),
                "course": course,
                "course_name": course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "user_name": user.name,
                "user_role": user.role,
                "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

                "success_message": success_message
            }
            return render(request, 'landing/team_creation.html', context)
            
        except Exception as e:
            all_students = course.members.filter(role='student')
            available_students = course.members.filter(role='student', teams__isnull=True)
            
            context = {
                "teams": course.teams.all(),
                "course": course,
                "course_name": course.name,
                "all_students": all_students,
                "available_students": available_students,
                "user": user,
                "user_name": user.name,
                "user_role": user.role,
                "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

                "error": f"An error occurred: {str(e)}"
            }
            return render(request, 'landing/team_creation.html', context)

class CreateCourseView(RequireAdminMixin, View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs['user']
        context = {
            'user_name': user.name,
            'user_role': user.role,
            "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",
        }
        return render(request, "landing/course_creation.html", context)
    
    def post(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs['user']
        course_name = request.POST.get('name')
        course_year = request.POST.get('year')
        course_semester = request.POST.get('semester')
        
        if course_name:
            try:
                course = create_new_course(course_name)
                course.members.add(user)
                user.courses.add(course)
                user.save()
 
                return redirect(reverse("landing:course_list") + "?success=course_created")
            except ValueError:
                context = {
                    'user_name': user.name,
                    'user_role': user.role,
                    "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",
                    'error': 'Invalid year'
                }
                return render(request, 'landing/course_creation.html', context)
        
        context = {
            'user_name': user.name,
            'user_role': user.role,
            "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",
        }
        return render(request, 'landing/course_creation.html', context)
    
class CourseListView(RequireLoggedInMixin, View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        
        if user.role == 'admin':
            courses = Course.objects.filter(members=user).prefetch_related('assessments')
        else:
            courses = Course.objects.filter(members=user).prefetch_related('assessments')
        
        context = {
            "user_name": user.name,
            "user_role": user.role,
            "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

            "courses": courses
        }
        
        success = request.GET.get('success')
        if success == 'course_created':
            context["success_message"] = "Course successfully created!"
            
        return render(request, "landing/course_list.html", context)