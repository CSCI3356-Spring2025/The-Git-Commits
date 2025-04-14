from django.http.request import QueryDict
from django.http.response import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.views import View
import datetime

from landing.models import Course, Team
from assessments.models import Assessment, AssessmentQuestion
from oauth.models import User
from django.db.models.query import QuerySet
from oauth.oauth import RequireLoggedInMixin, RequireAdminMixin

from itertools import chain

from django.shortcuts import render, redirect, get_object_or_404

from .models import StudentAssessmentResponse
from .feedback import get_feedback_summary, alphabetize_free_responses, average_likert_responses
from django.http.request import HttpRequest


class StudentAssessmentView(RequireLoggedInMixin, View):
    def get(self, request, *args, **kwargs):
        user = kwargs["user"]
        assessment_id = kwargs["assessment_id"]
        try:
            assessment = Assessment.objects.get(pk=assessment_id)
        except Assessment.DoesNotExist:
            return redirect(reverse("landing:dashboard"))

        # TODO: check that the user is in the course the assessment is intended for
        if assessment.course not in user.courses.all():
            return redirect(reverse("landing:dashboard"))

        current_team = user.teams.filter(course=assessment.course).first()
    
        context = {
            'assessment_title': assessment.title,
            'due_date': assessment.due_date,
            'questions': assessment.get_questions(),
            'user_name': user.name,
            'user_role': user.role
        }
        return render(request, 'student_assessment.html', context)

    def post(self, request, *args, **kwargs):
        user = kwargs["user"]
        assessment_id = kwargs["assessment_id"]
        
        try:
            assessment = Assessment.objects.get(pk=assessment_id)
        except Assessment.DoesNotExist:
            return redirect(reverse("landing:dashboard"))
        
        # Check that the user is in the course the assessment is intended for
        if assessment.course not in user.courses.all():
            return redirect(reverse("landing:dashboard"))
        
        current_team = user.teams.filter(course=assessment.course).first()
        if not current_team:
            messages.error(request, "You are not assigned to a team for this course.")
            return redirect(reverse("landing:dashboard"))
        
        # Get the evaluated team member from the form
        evaluated_user_email = request.POST.get("team_member_evaluated")
        try:
            evaluated_user = User.objects.get(email=evaluated_user_email)
        except User.DoesNotExist:
            messages.error(request, "Invalid team member selection")
            return redirect(reverse("landing:student_assessment", kwargs={"user": user, "assessment_id": assessment_id}))
        
        # Create the response record with the evaluated user
        response = StudentAssessmentResponse(
            student=user,
            assessment=assessment,
            evaluated_user=evaluated_user
        )
        response.save()
        
        # Process the answers for all other questions
        for question in assessment.get_questions():
            # Skip storing an answer for the team member selection question
            if question.question_type == 'team_member':
                continue
                
            answer_text = request.POST.get(f'question_{question.id}')
            answer = StudentAnswer(
                response=response, 
                question=question, 
                answer_text=answer_text
            )
            answer.save()
        
        messages.success(request, f"Assessment for {evaluated_user} submitted successfully!") # need naming
        return redirect('landing:student_assessment_list')

class StudentAssessmentListView(RequireLoggedInMixin, View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        assessments = list(chain.from_iterable(
            course.get_current_published_assessments()
            for course in user.courses.all()
        ))

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
    def get(self, request, *argv, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        course_id = request.GET.get('course_id')
        
        # If course_id is provided, use that specific course
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
            except Course.DoesNotExist:
                first_course = user.courses.first()
                if first_course is None:
                    return redirect(reverse("landing:dashboard"))
                course = first_course
        else:
            first_course = user.courses.first()
            if first_course is None:
                return redirect(reverse("landing:dashboard"))
            course = first_course

        # Determine which assessment this is for (creating a new one if necessary)
        assessment_id = request.session.get("assessment_id", None)
        if assessment_id:
            try:
                assessment = Assessment.objects.get(pk=assessment_id, course=course)
            except Assessment.DoesNotExist:
                assessment = Assessment.objects.create(
                    course=course, 
                    title="New Assessment", 
                    due_date=None, 
                    published=False
                )
                request.session["assessment_id"] = assessment.pk
        else:
            assessment = Assessment.objects.create(
                course=course, 
                title="New Assessment", 
                due_date=None, 
                published=False
            )
            request.session["assessment_id"] = assessment.pk

        context = {
            "assessment": assessment,
            "course": course,
            "user_name": user.name,
            "user_role": user.role,
            "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",
        }
        return render(request, "assessment_creation.html", context)

    def post(self, request, *argv, **kwargs) -> HttpResponse:
        """Buttons that have to update the page send POST requests back to update the database
        and re-render the page. Doing it this way instead of using basic JS (fetch or AJAX)
        feels like a war crime, but the requirements make it necessary.
        """
        user: User = kwargs["user"]
        course_id = request.POST.get('course_id')
        
        # If course_id is provided, use that specific course
        if course_id:
            try:
                course = Course.objects.get(pk=course_id)
                # Verify admin has access to this course
                if user.role != 'admin':
                    return redirect(reverse("landing:dashboard"))
            except Course.DoesNotExist:
                if not user.courses.exists():
                    return redirect(reverse("landing:dashboard"))
                course = user.courses.first()
        else:
            if not user.courses.exists():
                return redirect(reverse("landing:dashboard"))
            course = user.courses.first()

        # Determine which assessment this is for
        assessment_id = request.session.get("assessment_id", None)
        if assessment_id: 
            try:
                assessment = Assessment.objects.get(pk=assessment_id, course=course)
            except Assessment.DoesNotExist:
                assessment = Assessment.objects.create(
                    course=course,
                    title="New Assessment",
                    due_date=datetime.datetime.now() + datetime.timedelta(days=1),
                    published=False
                )
                request.session["assessment_id"] = assessment.pk
        else:
            assessment = Assessment.objects.create(
                course=course,
                title="New Assessment",
                # Default to tomorrow for now
                due_date=datetime.datetime.now() + datetime.timedelta(days=1),
                published=False
            )
            request.session["assessment_id"] = assessment.pk

        # Process the incoming action from the request data
        params = request.POST
        if params.get("add", None):
            self.handle_add(assessment)
        elif params.get("remove", None):
            self.handle_remove(assessment, params["remove"])
        elif params.get("edit", None):
            self.handle_edit(params)
        elif params.get("edit_assessment", None):
            self.handle_edit_assessment(assessment, params)
        elif params.get("publish", None):
            return self.handle_publish(request, assessment)

        context = { 
            "assessment": assessment,
            "course": course,
            "user_name": user.name,
            "user_role": user.role,
            # Why are we doing this thing below? It doesn't seem to get used at all
            "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",
        }
        return render(request, "assessment_creation.html", context)

    def handle_add(self, assessment: Assessment) -> None:
        # Get the count of existing questions for this assessment to determine the next order value
        next_order = assessment.questions.count()
        # Create the new question with the order value
        question = AssessmentQuestion.objects.create(
            assessment=assessment, 
            question_type="likert", 
            question="Question text?", 
            required=True,
            order=next_order
        )

    def handle_remove(self, assessment: Assessment, pk: str):
        AssessmentQuestion.objects.filter(pk=pk).delete()
        
        # After removing a question, reorder the remaining questions to ensure sequential ordering
        for i, question in enumerate(assessment.questions.all().order_by('order')):
            question.order = i
            question.save()

    def handle_edit(self, params: QueryDict):
        pk = str(params["edit"])
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

    def handle_edit_assessment(self, assessment: Assessment, params: QueryDict):
        title = params.get("assessment_title_edit", None)
        due_date = params.get("due_date", None)
        print(due_date)

        if title is not None:
            assessment.title = title
        if due_date is not None:
            try:
                assessment.due_date = datetime.datetime.strptime(due_date, "%Y-%m-%dT%H:%M")
            except ValueError:
                print("Could not parse time")
                pass
        assessment.save()


    def handle_publish(self, request: HttpRequest, assessment: Assessment) -> HttpResponse:
        assessment.published = True
        assessment.save()
        del request.session["assessment_id"]
        request.session.modified = True
        return redirect("landing:dashboard")
    

class CourseAssessmentsView(RequireLoggedInMixin, View):
    def get(self, request, *args, course_id="", **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        
        try:
            course = Course.objects.get(pk=course_id)
            if course not in user.courses.all() and user.role != 'admin':
                return redirect(reverse("landing:dashboard"))
                
            assessments = course.get_current_published_assessments()
            
            context = {
                "user_name": user.name,
                "user_role": user.role,
                "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",

                "course": course,
                "assessments": assessments
            }
            
            return render(request, "assessments/student_assessment_list.html", context)
            
        except Course.DoesNotExist:
            return redirect(reverse("landing:dashboard"))
        

class ProfessorCoursesView(RequireLoggedInMixin, View):
    """First page: List all courses taught by the professor"""
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        
        # Only admins should access this view
        if user.role != 'admin':
            return redirect('dashboard')
        
        # Get courses that have this professor as admin
        courses = Course.objects.filter(members=user)
        
        context = {
            "user_name": user.name,
            "user_role": user.role,
            "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",
            "courses": courses,
        }
        
        return render(request, "landing/professor_courses.html", context)

class ProfessorAssessmentsView(RequireLoggedInMixin, View):
    """Second page: List all assessments for a specific course"""
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        course_id = kwargs.get('course_id')
        
        if user.role != 'admin':
            return redirect('dashboard')
        
        course = get_object_or_404(Course, id=course_id, members=user)
        
        assessments = Assessment.objects.filter(course=course)
        
        context = {
            "user_name": user.name,
            "user_role": user.role,
            "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",
            "course": course,
            "assessments": assessments,
        }
        
        return render(request, "landing/professor_assessments.html", context)

class ProfessorTeamsView(RequireLoggedInMixin, View):
    """Third page: List all teams for a specific course and assessment"""
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        course_id = kwargs.get('course_id')
        assessment_id = kwargs.get('assessment_id')
        
        if user.role != 'admin':
            return redirect('dashboard')
        
        course = get_object_or_404(Course, id=course_id, members=user)
        assessment = get_object_or_404(Assessment, id=assessment_id, course=course)
        
        teams = Team.objects.filter(course=course)
        
        context = {
            "user_name": user.name,
            "user_role": user.role,
            "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",
            "course": course,
            "assessment": assessment,
            "teams": teams,
        }
        
        return render(request, "landing/professor_teams.html", context)

class ProfessorTeamFeedbackView(RequireLoggedInMixin, View):
    """Fourth page: Display raw feedback from team members for a specific assessment"""
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        course_id = kwargs.get('course_id')
        assessment_id = kwargs.get('assessment_id')
        team_id = kwargs.get('team_id')
        
        if user.role != 'admin':
            return redirect('dashboard')
        
        course = get_object_or_404(Course, id=course_id, members=user)
        assessment = get_object_or_404(Assessment, id=assessment_id, course=course)
        team = get_object_or_404(Team, id=team_id, course=course)
        
        team_members = team.members.all()
        
        responses = StudentAssessmentResponse.objects.filter(
            assessment=assessment,
            student__in=team_members
        ).select_related('student', 'evaluated_user')
        
        context = {
            "user_name": user.name,
            "user_role": user.role,
            "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",
            "course": course,
            "assessment": assessment,
            "team": team,
            "responses": responses,
        }
        
        return render(request, "landing/professor_team_feedback.html", context)

class StudentCoursesView(RequireLoggedInMixin, View):
    """First page: List all courses the student is enrolled in"""
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        
        # Only students should access this view
        if user.role != 'student':
            return redirect('dashboard')
        
        # Get courses that have this student as a member
        courses = user.courses.all()
        
        context = {
            "user_name": user.name,
            "user_role": user.role,
            "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",
            "courses": courses,
        }
        
        return render(request, "landing/student_courses.html", context)

class StudentAssessmentsView(RequireLoggedInMixin, View):
    """Second page: List all assessments for a specific course where the student was evaluated"""
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        course_id = kwargs.get('course_id')
        
        if user.role != 'student':
            return redirect('dashboard')
        
        course = get_object_or_404(Course, id=course_id, members=user)
        
        assessments = Assessment.objects.filter(
            course=course,
            studentassessmentresponse__evaluated_user=user
        ).distinct()
        
        context = {
            "user_name": user.name,
            "user_role": user.role,
            "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",
            "course": course,
            "assessments": assessments,
        }
        
        return render(request, "landing/student_assessments.html", context)

class StudentFeedbackView(RequireLoggedInMixin, View):
    """Third page: Display processed feedback for a specific assessment"""
    def get(self, request, *args, **kwargs) -> HttpResponse:
        user: User = kwargs["user"]
        course_id = kwargs.get('course_id')
        assessment_id = kwargs.get('assessment_id')
        
        if user.role != 'student':
            return redirect('dashboard')
        
        course = get_object_or_404(Course, id=course_id, members=user)
        assessment = get_object_or_404(Assessment, id=assessment_id, course=course)
        
        feedback_summary = get_feedback_summary(evaluated_user=user, assessment=assessment)
        
        context = {
            "user_name": user.name,
            "user_role": user.role,
            "user_team": ", ".join(team.name for team in user.teams.all()) if user.teams.exists() else "",
            "course": course,
            "assessment": assessment,
            "feedback": feedback_summary,
        }
        
        return render(request, "landing/student_feedback.html", context)
