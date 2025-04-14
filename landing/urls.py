from django.urls import path
from . import views
from assessments.views import ProfessorCoursesView, StudentCoursesView

app_name = "landing"

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('team_creation/', views.CreateTeamView.as_view(), name='team_creation'),
    path('course_creation/', views.CreateCourseView.as_view(), name='course_creation'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('professor/courses/', ProfessorCoursesView.as_view(), name='professor_courses'),
    path('student/courses/', StudentCoursesView.as_view(), name='student_courses')
]
