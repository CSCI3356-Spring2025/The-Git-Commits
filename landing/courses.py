from models import Course, Team
from oauth.models import User

def create_new_course(name: str, year: int) -> Course:
    course = Course(name, year)
    course.save()
    return course

def create_new_team(name: str, course_name: int) -> Team:
    # TODO: we should probably have this take a course primary key instead
    # but this works for now and will be easier to hook into the webpage
    course = Course.objects.get(name=course_name)
    team = Team(name, course=course)
    team.save()
    return team

def add_student_to_course(student_email: str, course_name: str) -> bool:
    try:
        student = User.objects.get(email=student_email)
        course = Course.objects.get(name=course_name)
        student.course = course
        student.save()
        return True
    except (User.DoesNotExist, Course.DoesNotExist):
        return False

def add_student_to_team(student_email: str, team_name: str) -> bool:
    try:
        student = User.objects.get(email=student_email)
        team = Team.objects.get(name=team_name)
        student.team = team
        student.save()
        return True
    except (User.DoesNotExist, Team.DoesNotExist):
        return False

def remove_student_from_course(student_email: str) -> bool:
    try:
        student = User.objects.get(email=student_email)
        student.course = None
        student.save()
        return True
    except User.DoesNotExist:
        return False

def remove_student_from_team(student_email: str) -> bool:
    try:
        student = User.objects.get(email=student_email)
        student.team = None
        student.save()
        return True
    except User.DoesNotExist:
        return False

def remove_course(course_name: str) -> bool:
    try:
        course = Course.objects.get(name=course_name)
        # First remove all students from the course
        for student in course.members.all():
            student.course = None
            student.save()
        # Delete the course (this will cascade delete teams due to the CASCADE setting)
        course.delete()
        return True
    except Course.DoesNotExist:
        return False

def remove_team(team_name: str) -> bool:
    try:
        team = Team.objects.get(name=team_name)
        # First remove all students from the team
        for student in team.members.all():
            student.team = None
            student.save()
        # Delete the team
        team.delete()
        return True
    except Team.DoesNotExist:
        return False
