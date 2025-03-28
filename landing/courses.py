from models import Course, Team

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
