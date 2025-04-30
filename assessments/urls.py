from django.urls import path
from . import views

app_name = "assessments"

urlpatterns = [
    path('assessment/<int:assessment_id>/', views.StudentAssessmentView.as_view(), name='student_assessment'),
    path('assessment_list/', views.StudentAssessmentListView.as_view(), name='student_assessment_list'),
    path('assessment_creation/', views.CreateAssessmentView.as_view(), name='assessment_creation'),
    
    path('course/<int:course_id>/assessments/', views.CourseAssessmentsView.as_view(), name='student_course_assessment_list'),

    path('professor_assessments/', views.ProfessorAssessmentListView.as_view(), name='professor_assessment_list'),
]

"""
    path('professor/courses/', views.ProfessorFeedbackCoursesView.as_view(), name='professor_courses'),
    path('professor/courses/<int:course_id>/assessments/', views.ProfessorAssessmentsView.as_view(), name='professor_assessments'),
    path('professor/courses/<int:course_id>/assessments/<int:assessment_id>/teams/', views.ProfessorFeedbackTeamsView.as_view(), name='professor_teams'),
    path('professor/courses/<int:course_id>/assessments/<int:assessment_id>/teams/<int:team_id>/feedback/', views.ProfessorIndividualFeedbackView.as_view(), name='professor_team_feedback'),
    path('student/courses/', views.StudentCoursesView.as_view(), name='student_courses'),
    path('student/courses/<int:course_id>/assessments/', views.StudentAssessmentsView.as_view(), name='student_assessments'),
"""
