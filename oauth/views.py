from oauth.oauth import is_logged_in
from oauth.oauth import handle_oauth_callback
from django.views import View
from django.http.response import HttpResponse
from django.template.response import TemplateResponse
from django.views.generic.base import TemplateView
import google.oauth2.credentials
import google_auth_oauthlib.flow
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse
from . import oauth
from django.http.response import JsonResponse
from django.contrib.auth import login, logout
from django.template.loader import get_template
from oauth.oauth import get_role
from oauth.models import User
from oauth.oauth import get_logged_in_user

class RegistrationView(View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        # Ensure the user has verified an email through OAuth
        if not request.session.get("email", False):
            return redirect("login")

        context = {}
        return TemplateResponse(request, "oauth/student_creation.html", context)

class RegistrationCallbackView(View):
    # This should only receive POSTs
    def get(self, request, *args, **kwargs) -> HttpResponse:
        return redirect(reverse("landing:dashboard"))

    def post(self, request, *args, **kwargs) -> HttpResponse:
        return oauth.register_user(request)


class AuthView(View):
    """Starts the OAuth authorization flow and redirects to Google for login/authorization"""
    def get(self, request, *args, **kwargs) -> HttpResponse:
        if is_logged_in(request):
            return redirect(reverse("landing:dashboard"))

        redirect_uri=request.build_absolute_uri(reverse('oauth:callback'))
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(settings.OAUTH_CLIENT_SECRET_PATH,
                                                                       scopes=["https://www.googleapis.com/auth/userinfo.email openid"],
                                                                       redirect_uri=redirect_uri)
        authorization_url, state = flow.authorization_url(
            # Allow refreshing an access token without re-prompting the user for permission.
            access_type='offline',
            # Enable incremental authorization. Recommended by Google as a best practice.
            include_granted_scopes='true')
        return redirect(authorization_url)

class CallbackView(View):
    def get(self, request, *args, **kwargs) -> HttpResponse:
        next_redirect = handle_oauth_callback(request)
        if next_redirect is None:
            # TODO make this show an invalid login message to the user
            return redirect(reverse("landing:landing_page"))
        return next_redirect

class LogoutView(View):
    """Handles user logout by clearing the session and redirecting to login page"""
    def get(self, request, *args, **kwargs) -> HttpResponse:
        # Clear all session data
        request.session.flush()
        # Redirect to login page
        return redirect(reverse("oauth:auth"))
