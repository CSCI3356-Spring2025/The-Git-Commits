from django.urls import path
from . import views

app_name = "landing"

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('assessment/<int:assessment_id>/', views.StudentAssessmentView.as_view(), name='student_assessment'),
    path('assessment_list/', views.StudentAssessmentListView.as_view(), name='student_assessment_list'),
    path('assessment_creation/', views.CreateAssessmentView.as_view(), name='assessment_creation'),
    path('team_creation/', views.CreateTeamView.as_view(), name='team_creation'),
    path('course_creation/', views.CreateCourseView.as_view(), name='course_creation'),
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('review_feedback/', views.ReviewFeedbackView.as_view(), name='review_feedback'),
]
