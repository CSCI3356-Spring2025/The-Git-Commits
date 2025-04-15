from django.urls import path
from . import views
from assessments.views import ProfessorCoursesView, StudentCoursesView, ProfessorAssessmentsView, ProfessorTeamsView, ProfessorTeamFeedbackView, StudentAssessmentsView, StudentFeedbackView

app_name = "landing"

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('team_creation/', views.CreateTeamView.as_view(), name='team_creation'),
    path('course_creation/', views.CreateCourseView.as_view(), name='course_creation'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),

    path('professor/courses/', ProfessorCoursesView.as_view(), name='professor_courses'),
    path('student/courses/', StudentCoursesView.as_view(), name='student_courses'),

    path('professor/courses/<int:course_id>/assessments/', ProfessorAssessmentsView.as_view(), name='professor_assessments'),
    path('professor/courses/<int:course_id>/assessments/<int:assessment_id>/teams/', ProfessorTeamsView.as_view(), name='professor_teams'),
    path('professor/courses/<int:course_id>/assessments/<int:assessment_id>/teams/<int:team_id>/students/<int:student_id>/feedback/', ProfessorTeamFeedbackView.as_view(), name='professor_team_feedback'),
    path('student/courses/<int:course_id>/assessments/', StudentAssessmentsView.as_view(), name='student_assessments'),
    path('student/courses/<int:course_id>/assessments/<int:assessment_id>/feedback/', StudentFeedbackView.as_view(), name='student_feedback'),
]
