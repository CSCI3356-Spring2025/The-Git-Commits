import google_auth_oauthlib.flow
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.shortcuts import redirect
from django.urls import reverse
from googleapiclient.discovery import build

from .models import User
from oauth.models import Course
from peervue.settings import OAUTH_CLIENT_SECRET_PATH
from google.oauth2 import id_token
from google_auth_httplib2 import Request
from google.auth.transport import requests


def get_email(credentials) -> str:
    user_info_service = build('oauth2', 'v2', credentials=credentials)
    user_info = user_info_service.userinfo().get().execute()
    return user_info["email"]


def get_credentials(request):
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.OAUTH_CLIENT_SECRET_PATH,
        scopes=None,
        redirect_uri=redirect_uri)

    code = request.GET.get("code", "")
    if code == "":
        return None

    flow.fetch_token(code=code)
    return flow.credentials


def verify_email(email: str) -> bool:
    return email.endswith("@bc.edu")


def get_role(email: str) -> str:
    if email in settings.VERIFIED_ADMIN_EMAILS:
        return "admin"
    return "student"


def handle_oauth_callback(request):
    credentials = get_credentials(request)
    if not credentials:
        return None

    email = get_email(credentials)
    if not verify_email(email):
        return None

    role = get_role(email)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Redirect newly created users to registration
        # We'll need these to update the model in registration
        request.session["email"] = email
        request.session["role"] = role
        request.session["token"] = credentials.token
        return redirect(reverse("registration"))

    if not login(request, user, credentials.token):
        return redirect(reverse("login"))

    return redirect(reverse("landing"))


def register_user(request):
    """Completes the user registration flow, adding the user to the database and logging in"""

    email = request.session.get("email", False)
    role = request.session.get("role", False)
    token = request.session.get("token", False)
    if not (email and role and token):
        return HttpResponse(f"email: {email}\nrole: {role}\ntoken: {token}")
        # return redirect(reverse("login"))

    name = request.POST.get("name", False)
    course_id = request.POST.get("course", False)
    if not (name and course_id):
        # This should only happen if the user tries to maliciously manufacture a request
        return redirect(reverse("registration"))

    course = Course.objects.get(id=course_id)
    if not course:
        return redirect(reverse("registration"))

    del request.session["email"]
    del request.session["role"]
    del request.session["token"]

    user = User.objects.create(name=name, email=email, course=course, role=role)
    user.save()
    if not login(request, user, token):
        return redirect(reverse("login"))
    

    return redirect(reverse("landing"))
     
def login(request, user, token):
    """Sets the user's session as logged in"""
    request.session["user"] = user.pk
    request.session["logged_in"] = True

    return True

def is_logged_in(request) -> bool:
    """Checks if request is from a logged in user"""
    if not request.session.get("logged_in", False):
        return False
    
    user_pk = request.session.get("user", False)
    if not user_pk:
        return False

    # We should make sure the user is in the database in case the user has been removed
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return False

    return True

class RequireLoggedInMixin:
    """Django view mixin to require that the user is logged in,
    otherwise it redirects them to the login page."""

    login_url = None

    def get_login_url(self) -> str:
        if self.login_url:
            return self.login_url
        return reverse("login")

    def dispatch(self, request, *args, **kwargs):
        if not is_logged_in(request):
            return redirect(self.get_login_url())
        return super().dispatch(request, *args, **kwargs)

