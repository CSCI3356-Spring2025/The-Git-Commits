from django.urls import path
from . import views

app_name = "landing"

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('assessment/', views.student_assessment_view, name='student_assessment'),
]
