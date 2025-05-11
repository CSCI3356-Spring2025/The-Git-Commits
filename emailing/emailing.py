import datetime
from django.core.mail import send_mass_mail, send_mail
from django.db.models.query import Prefetch
from django.template.loader import render_to_string
from assessments.models import Assessment
from oauth.models import User
from django.shortcuts import render
from django.utils import timezone

TIME_DELTA = datetime.timedelta(minutes=5)

def check_and_send():
    time_now = timezone.now()
    assessments_by_publish = Assessment.objects.filter(
        publish_date__lte=time_now,
        publish_email_sent=False
    ).prefetch_related("course__members")

    emails = ()

    for assessment in assessments_by_publish:
        addresses = assessment.course.members.values_list("email", flat=True)

        assessment_name = assessment.title
        course_name = assessment.course.name

        context = { "course_name": course_name, "assessment_name": assessment_name }
        email_text = render_to_string("publish_email.html", context)

        emails = (*emails, (
            "PeerVue: Assessment Published",
            email_text,
            "PeerVue",
            addresses,
        ))
        assessment.publish_email_sent = True
        assessment.save()

    assessments_by_due = Assessment.objects.filter(
        due_date__lte=time_now + TIME_DELTA,
        due_soon_email_sent=False
    ).prefetch_related("course__members")

    for assessment in assessments_by_due:
        addresses = assessment.course.members.values_list("email", flat=True)

        assessment_name = assessment.title
        course_name = assessment.course.name

        context = { "course_name": course_name, "assessment_name": assessment_name }
        email_text = render_to_string("due_soon_email.html", context)

        emails = (*emails, (
            "Assessment Due Soon",
            email_text,
            "PeerVue",
            addresses,
        ))
        assessment.due_soon_email_sent = True
        assessment.save()

    send_mass_mail(emails, fail_silently=False)

def send_email_invite(email: str, course_name: str, login_url: str):
    context = { "course_name": course_name, "login_url": login_url }
    email_text = render_to_string("invite_email.html", context)

    send_mail("PeerVue: Course Invitation", email_text, "PeerVue", (email,))
