from django.urls import path
from . import views

app_name = "assessments"

urlpatterns = [
    path('assessment/<int:assessment_id>/', views.StudentAssessmentView.as_view(), name='student_assessment'),
    path('assessment_list/', views.StudentAssessmentListView.as_view(), name='student_assessment_list'),
    path('assessment_creation/', views.CreateAssessmentView.as_view(), name='assessment_creation'),

    # Why is some of this here when there's already a courses view in the landing app?
    # Most of it tries to render a template that doesn't exist, or one that's
    # already in the landing app
    path('professor/courses/', views.ProfessorCoursesView.as_view(), name='professor_courses'),
    path('professor/courses/<int:course_id>/assessments/', views.ProfessorAssessmentsView.as_view(), name='professor_assessments'),
    path('professor/courses/<int:course_id>/assessments/<int:assessment_id>/teams/', views.ProfessorTeamsView.as_view(), name='professor_teams'),
    path('professor/courses/<int:course_id>/assessments/<int:assessment_id>/teams/<int:team_id>/feedback/', views.ProfessorTeamFeedbackView.as_view(), name='professor_team_feedback'),
    path('student/courses/', views.StudentCoursesView.as_view(), name='student_courses'),
    path('student/courses/<int:course_id>/assessments/', views.StudentAssessmentsView.as_view(), name='student_assessments'),
    path('student/courses/<int:course_id>/assessments/<int:assessment_id>/feedback/', views.StudentFeedbackView.as_view(), name='student_feedback'),
    
    path('course/<int:course_id>/assessments/', views.CourseAssessmentsView.as_view(), name='student_course_assessment_list'),
]
