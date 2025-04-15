from django.urls import path
from . import views
from assessments.views import ProfessorFeedbackCoursesView, StudentCourseListView, ProfessorFeedbackAssessmentsView, ProfessorFeedbackTeamsView, ProfessorIndividualFeedbackView, StudentAssessmentView, StudentFeedbackView

app_name = "landing"

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('team_creation/', views.CreateTeamView.as_view(), name='team_creation'),
    path('course_creation/', views.CreateCourseView.as_view(), name='course_creation'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),

    path('professor/feedback/', ProfessorFeedbackCoursesView.as_view(), name='professor_feedback_courses'),
    path('professor/feedback/<int:course_id>/', ProfessorFeedbackAssessmentsView.as_view(), name='professor_feedback_assessments'),
    path('professor/feedback/<int:course_id>/<int:assessment_id>/', ProfessorFeedbackTeamsView.as_view(), name='professor_feedback_teams'),
    path('professor/feedback/<int:course_id>/<int:assessment_id>/<int:team_id>/feedback/', ProfessorIndividualFeedbackView.as_view(), name='professor_feedback_individual'),
    
    path('student/courses/', StudentCourseListView.as_view(), name='student_courses'),
    path('student/courses/<int:course_id>/assessments/', StudentAssessmentView.as_view(), name='student_assessments'),
    path('student/courses/<int:course_id>/assessments/<int:assessment_id>/feedback/', StudentFeedbackView.as_view(), name='student_feedback'),
]
