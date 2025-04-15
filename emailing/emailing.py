from django.core.mail import send_mass_mail
from assessments.models import Assessment
import datetime
from django.db.models.query import Prefetch
from oauth.models import User

TIME_DELTA = datetime.timedelta(hours=24)

def check_and_send():
    time_now = datetime.datetime.now()
    assessments_by_publish = Assessment.objects.filter(
        publish_date__lte=time_now,
        publish_email_sent=False
    ).prefetch_related("course__members")

    emails = ()
    for assessment in assessments_by_publish:
        addresses = assessment.course.members.values_list("email", flat=True)
        # TODO: Render HTML template
        emails = (*emails, (
            "Assessment Published",
            "An assessment was published.",
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
        # TODO: Render HTML template
        emails = (*emails, (
            "Assessment Due Soon",
            "An assessment is due soon.",
            "PeerVue",
            addresses,
        ))
        assessment.due_soon_email_sent = True
        assessment.save()

    send_mass_mail(emails, fail_silently=False)
