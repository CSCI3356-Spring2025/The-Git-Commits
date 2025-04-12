from .models import Course, Team
from oauth.models import User
import datetime

def create_new_course(name: str) -> Course:
    current_month = datetime.datetime.now().month
    year = datetime.datetime.now().year
    if 1 <= current_month <= 5:
        semester = "Spring"
    elif 6 <= current_month <= 8:
        semester = "Summer"
    else:
        semester = "Fall"
    course = Course.objects.create(name=name, year=year, semester=semester)
    return course

def create_new_team(name: str, course_name: str) -> Team:
    # TODO: we should probably have this take a course primary key instead
    # but this works for now and will be easier to hook into the webpage
    course = Course.objects.get(name=course_name)
    team = Team.objects.create(name=name, course=course)
    team.save()
    return team

def add_student_to_course(student_email: str, course_name: str) -> bool:
    try:
        student = User.objects.get(email=student_email)
        course = Course.objects.get(name=course_name)
        course.members.add(student)
        return True
    except (User.DoesNotExist, Course.DoesNotExist):
        return False

def add_student_to_team(student_email: str, team_name: str) -> bool:
    try:
        student = User.objects.get(email=student_email)
        team = Team.objects.get(name=team_name)
        team.members.add(student)
        return True
    except (User.DoesNotExist, Team.DoesNotExist):
        return False

def remove_student_from_course(student_email: str) -> bool:
    try:
        student = User.objects.get(email=student_email)
        course = Course.objects.get(name=course_name)
        course.members.remove(student)
        return True
    except User.DoesNotExist:
        return False

def remove_student_from_team(student_email: str) -> bool:
    try:
        student = User.objects.get(email=student_email)
        team = Team.objects.get(name=course_name)
        team.members.remove(student)
        return True
    except User.DoesNotExist:
        return False

def remove_course(course_name: str) -> bool:
    try:
        course = Course.objects.get(name=course_name)
        course.delete()
        return True
    except Course.DoesNotExist:
        return False

def remove_team(team_name: str) -> bool:
    try:
        team = Team.objects.get(name=team_name)
        team.delete()
        return True
    except Team.DoesNotExist:
        return False
