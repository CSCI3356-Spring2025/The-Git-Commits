from django.urls import path
from . import views

app_name = "landing"

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('assessment/<int:assessment_id>/', views.StudentAssessmentView.as_view(), name='student_assessment'),
    path('assessment_list/', views.StudentAssessmentListView.as_view(), name='student_assessment_list'),
    path('team_creation/', views.TeamEditView.as_view(), name='team_creation'),
]
