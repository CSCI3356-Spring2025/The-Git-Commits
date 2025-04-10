from django.http.response import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.views import View
import datetime

from landing.models import Course, Team
from assessments.models import Assessment, AssessmentQuestion
from oauth.models import User
from django.db.models.query import QuerySet
from oauth.oauth import RequireLoggedInMixin, RequireAdminMixin


class StudentAssessmentView(RequireLoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        user = kwargs["user"]
        assessment_id = kwargs["assessment_id"]
        try:
            assessment = Assessment.objects.get(pk=assessment_id)
        except Assessment.DoesNotExist:
            return redirect(reverse("landing:dashboard"))

        # TODO: check that the user is in the course the assessment is intended for
        if user.course != assessment.course:
            return redirect(reverse("landing:dashboard"))

        context = {
            'assessment_title': assessment.title,
            'due_date': assessment.due_date,
            'questions': assessment.get_questions(),
            'user_name': user.name,
            'user_role': user.role
        }
        return render(request, 'new_student_assessment.html', context)

    def post(self, request, *args, **kwargs):
        return redirect('landing:student_assessment_list')

class StudentAssessmentListView(RequireLoggedInMixin, View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        if user.course:
            assessments = user.course.get_current_published_assessments()
        else:
            assessments = Assessment.objects.none()

        context = {
            "user_name": user.name,
            "user_role": user.role,
            "assessments": assessments
        }
        return render(request, "student_assessment_list.html", context)
    def post(self, request, *args, **kwargs):
        #TODO: We can process the data from the form here later
        return redirect(reverse('assessments:student_assessment_list'))


class CreateAssessmentView(RequireAdminMixin, View):
    # Right now we're assuming this will create a new assessment, not edit an existing one
    # because creation was in the requirements but not editing
    def get(self, request, *argv, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        if user.course is None:
            return redirect(reverse("landing:dashboard"))

        # Determine which assessment this is for (creating a new one if necessary)
        assessment_id = request.session.get("assessment_id", None)
        if assessment_id:
            assessment = Assessment.objects.get(pk=assessment_id)
        else:
            assessment = Assessment.objects.create(course = user.course, title="New Assessment", due_date=None, published=False)
            request.session["assessment_id"] = assessment.pk

        context = {"assessment": assessment}
        return render(request, "assessment_creation.html", context)

    def post(self, request, *argv, **kwargs) -> HttpResponse:
        """Buttons that have to update the page send POST requests back to update the database
        and re-render the page. Doing it this way instead of using basic JS feels like a war crime,
        but the requirements make it necessary.
        """
        user: User = kwargs["user"]
        if user.course is None:
            return redirect(reverse("landing:dashboard"))

        # Determine which assessment this is for
        assessment_id = request.session.get("assessment_id", None)
        if assessment_id: 
            assessment = Assessment.objects.get(pk=assessment_id)
        else:
            assessment = Assessment.objects.create(
                course = user.course,
                title="New Assessment",
                # Default to tomorrow for now
                due_date=datetime.datetime.now() + datetime.timedelta(days=1),
                published=False
            )
            request.session["assessment_id"] = assessment.pk

        # Process the incoming action from the request data
        # TODO: factor this out into another function
        params = request.POST
        if params.get("add", None):
            question = AssessmentQuestion.objects.create(assessment=assessment, question_type="likert", question="Question text?", required=True)

        elif params.get("remove", None):
            pk = params["remove"]
            AssessmentQuestion.objects.filter(pk=pk).delete()

        elif params.get("edit", None):
            pk = params["edit"]
            question = AssessmentQuestion.objects.get(pk=pk)

            required = params.get("required", None)
            question_text = params.get("question", None)
            question_type = params.get("question_type", None)
            if required is not None:
                question.required = (required == "on")
            if question_text is not None:
                question.question = question_text
            if question_type == "likert" or question_type == "free":
                question.question_type = question_type

            question.save()

        elif params.get("publish", None):
            assessment.published = True
            assessment.save()
            del request.session["assessment_id"]
            request.session.modified = True
            return redirect("landing:dashboard")


        context = { "assessment": assessment }
        return render(request, "assessment_creation.html", context)
    
    
class ReviewFeedbackView(RequireLoggedInMixin, View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        
        context = {
            "user_name": user.name,
            "user_role": user.role,
            "user_team": user.team.name if user.team else "",
        }
        
        return render(request, "review_feedback.html", context)
    
class ViewFeedbackView(RequireLoggedInMixin, View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        
        context = {
            "user_name": user.name,
            "user_role": user.role,
            "user_team": user.team.name if user.team else "",
        }
        
        return render(request, "view_feedback.html", context)
