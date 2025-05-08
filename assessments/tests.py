from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
import datetime
from oauth.models import User, AdminEmailAddress
from landing.models import Course, Team
from assessments.models import Assessment, AssessmentQuestion, StudentAssessmentResponse, StudentAnswer

class AssessmentSystemTests(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_email = "professor@bc.edu"
        AdminEmailAddress.objects.create(email=self.admin_email)
        self.admin = User.objects.create(
            name="Professor Smith",
            email=self.admin_email,
            role="admin",
            is_active=True,
            is_staff=True,
            is_superuser=True,
            password="testpass123"
        )

        # Create student users
        self.student1 = User.objects.create(
            name="Student One",
            email="student1@bc.edu",
            role="student",
            is_active=True,
            password="testpass123"
        )
        self.student2 = User.objects.create(
            name="Student Two",
            email="student2@bc.edu",
            role="student",
            is_active=True,
            password="testpass123"
        )
        self.student3 = User.objects.create(
            name="Student Three",
            email="student3@bc.edu",
            role="student",
            is_active=True,
            password="testpass123"
        )

        # Create course
        self.course = Course.objects.create(
            name="Test Course",
            year="2024",
            semester="Spring"
        )
        self.course.members.add(self.admin, self.student1, self.student2, self.student3)

        # Create team
        self.team = Team.objects.create(
            name="Team A",
            course=self.course
        )
        self.team.members.add(self.student1, self.student2, self.student3)

        # Create assessment
        self.assessment = Assessment.objects.create(
            title="Test Assessment",
            course=self.course,
            publish_date=timezone.now() - datetime.timedelta(days=1),
            due_date=timezone.now() + datetime.timedelta(days=7),
            allow_self_assessment=True
        )

        # Create questions
        self.likert_question = AssessmentQuestion.objects.create(
            assessment=self.assessment,
            question="How well did they contribute?",
            question_type="likert",
            required=True,
            order=1
        )
        self.free_question = AssessmentQuestion.objects.create(
            assessment=self.assessment,
            question="What could they improve?",
            question_type="free",
            required=True,
            order=2
        )

        # Setup client
        self.client = Client()

    def login_user(self, user):
        """Helper method to set up session data for a user"""
        session = self.client.session
        session['logged_in'] = True
        session['user'] = user.email  # Use email as the identifier since it's our primary key
        session.save()
        # Don't use force_login since we have our own auth system

    def test_end_to_end_assessment_flow(self):
        """Test the complete flow from assessment creation to results publication"""
        # 1. Admin creates assessment
        self.login_user(self.admin)
        
        # First get the page to set up session
        response = self.client.get(
            reverse('assessments:assessment_creation'),
            {'course_id': self.course.id}
        )
        self.assertEqual(response.status_code, 200)
        
        # Now add a question
        response = self.client.post(
            reverse('assessments:assessment_creation'),
            {
                'course_id': self.course.id,
                'add': 'question'
            }
        )
        self.assertEqual(response.status_code, 200)

        # Get the latest question
        latest_question = AssessmentQuestion.objects.latest('id')
        
        # Edit the question
        response = self.client.post(
            reverse('assessments:assessment_creation'),
            {
                'course_id': self.course.id,
                'edit': latest_question.id,
                'question': 'New Question',
                'question_type': 'likert',
                'required': 'on'
            }
        )
        self.assertEqual(response.status_code, 200)

        # 2. Students submit assessments
        self.login_user(self.student1)
        
        # First try submitting without required answers
        response = self.client.post(
            reverse('assessments:student_assessment', args=[self.assessment.id]),
            {
                'team_member_evaluated': self.student2.email,
                # Missing required questions
            }
        )
        self.assertEqual(response.status_code, 302)  # Should redirect back to form
        
        # Now submit with all required answers
        response = self.client.post(
            reverse('assessments:student_assessment', args=[self.assessment.id]),
            {
                'team_member_evaluated': self.student2.email,
                f'question_{self.likert_question.id}': '4',
                f'question_{self.free_question.id}': 'Good work!'
            }
        )
        self.assertEqual(response.status_code, 302)  # Redirect after successful submission

        # Verify the response was created
        self.assertTrue(StudentAssessmentResponse.objects.filter(
            student=self.student1,
            assessment=self.assessment,
            evaluated_user=self.student2
        ).exists())

        # 3. Admin publishes results
        self.login_user(self.admin)

        # Navigate through the feedback flow
        response = self.client.get(
            reverse('landing:professor_feedback_courses')
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('landing:professor_feedback_assessments', args=[self.course.id])
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('landing:professor_feedback_teams', args=[self.course.id, self.assessment.id])
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            reverse('landing:professor_feedback_individual', args=[self.course.id, self.assessment.id, self.team.id])
        )
        self.assertEqual(response.status_code, 200)

        # Publish feedback from the final view
        response = self.client.post(
            reverse('landing:professor_feedback_final', args=[self.course.id, self.assessment.id, self.team.id, self.student2.email]),
            {
                'publish_results': True
            }
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to professor_feedback_courses

        # Verify the assessment is marked as published
        self.assessment.refresh_from_db()
        self.assertTrue(self.assessment.responses_published)

        # 4. Student views results
        self.login_user(self.student2)
        response = self.client.get(
            reverse('landing:student_feedback', args=[self.course.id, self.assessment.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Good work!')

    def test_edge_cases(self):
        """Test various edge cases and error conditions"""
        # 1. Test assessment submission after deadline
        self.assessment.due_date = timezone.now() - datetime.timedelta(days=1)
        self.assessment.save()
        
        self.login_user(self.student1)
        response = self.client.post(
            reverse('assessments:student_assessment', args=[self.assessment.id]),
            {
                'team_member_evaluated': self.student2.email,
                f'question_{self.likert_question.id}': '4',
                f'question_{self.free_question.id}': 'Good work!'
            }
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to dashboard

        # Verify no response was created
        self.assertFalse(StudentAssessmentResponse.objects.filter(
            student=self.student1,
            assessment=self.assessment
        ).exists())

        # 2. Test self-assessment when not allowed
        self.assessment.allow_self_assessment = False
        self.assessment.save()
        
        response = self.client.post(
            reverse('assessments:student_assessment', args=[self.assessment.id]),
            {
                'team_member_evaluated': self.student1.email,  # Try to self-assess
                f'question_{self.likert_question.id}': '4',
                f'question_{self.free_question.id}': 'Good work!'
            }
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to dashboard

        # Verify no response was created
        self.assertFalse(StudentAssessmentResponse.objects.filter(
            student=self.student1,
            assessment=self.assessment,
            evaluated_user=self.student1
        ).exists())

        # 3. Test assessment submission before publish date
        self.assessment.publish_date = timezone.now() + datetime.timedelta(days=1)
        self.assessment.save()
        
        response = self.client.get(
            reverse('assessments:student_assessment', args=[self.assessment.id])
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to dashboard

        # 4. Test viewing results before publication
        self.assessment.responses_published = False
        self.assessment.save()
        
        response = self.client.get(
            reverse('landing:student_feedback', args=[self.course.id, self.assessment.id])
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to dashboard

    def test_team_management(self):
        """Test team-related edge cases"""
        # Test creating a team without a name
        self.login_user(self.admin)
        response = self.client.post(
            reverse('landing:team_creation'),
            {
                'action': 'create_team',
                'course_id': self.course.id,
                'member_emails': [self.student1.email]
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Team name is required")

        # Test creating a team with a name
        response = self.client.post(
            reverse('landing:team_creation'),
            {
                'action': 'create_team',
                'course_id': self.course.id,
                'name': 'Test Team',
                'member_emails': [self.student1.email]
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Team &#x27;Test Team&#x27; created successfully!")

        # Test adding a student to the course
        response = self.client.post(
            reverse('landing:team_creation'),
            {
                'action': 'add_student',
                'course_id': self.course.id,
                'student_name': 'New Student',
                'student_email': 'new.student@bc.edu'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Student &#x27;New Student&#x27; created and added to course!")

    def test_assessment_validation(self):
        """Test assessment validation and constraints"""
        # 1. Test required questions
        self.login_user(self.student1)
        response = self.client.post(
            reverse('assessments:student_assessment', args=[self.assessment.id]),
            {
                'team_member_evaluated': self.student2.email,
                # Missing required questions
            }
        )
        self.assertEqual(response.status_code, 302)  # Should redirect back to form with errors
        
        # 2. Test invalid Likert scale values
        response = self.client.post(
            reverse('assessments:student_assessment', args=[self.assessment.id]),
            {
                'team_member_evaluated': self.student2.email,
                f'question_{self.likert_question.id}': '6',  # Invalid value
                f'question_{self.free_question.id}': 'Good work!'
            }
        )
        self.assertEqual(response.status_code, 302)  # Should redirect back to form with errors

    def test_course_access(self):
        """Test course access restrictions"""
        # Create another course and student
        other_course = Course.objects.create(
            name="Other Course",
            year="2024",
            semester="Spring"
        )
        other_student = User.objects.create(
            name="Other Student",
            email="other@bc.edu",
            role="student",
            is_active=True,
            password="testpass123"
        )
        other_course.members.add(other_student)

        # Test student trying to access assessment from different course
        self.login_user(other_student)
        response = self.client.get(
            reverse('assessments:student_assessment', args=[self.assessment.id])
        )
        self.assertEqual(response.status_code, 302)  # Should redirect to dashboard

