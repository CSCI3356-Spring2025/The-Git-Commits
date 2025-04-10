from django.urls import path
from . import views

app_name = "assessments"

urlpatterns = [
    path('assessment/<int:assessment_id>/', views.StudentAssessmentView.as_view(), name='student_assessment'),
    path('assessment_list/', views.StudentAssessmentListView.as_view(), name='student_assessment_list'),
    path('assessment_creation/', views.CreateAssessmentView.as_view(), name='assessment_creation'),
    path('review_feedback/', views.ReviewFeedbackView.as_view(), name='review_feedback'),
    path('view_feedback/', views.ViewFeedbackView.as_view(), name='view_feedback'),
]
