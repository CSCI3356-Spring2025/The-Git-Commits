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
from oauth.models import Course
from django.contrib.auth import login
from django.template.loader import get_template

class LoginView(View):
    def get(self, request, *args, **kwargs):
        if oauth.is_logged_in(request):
            return redirect(reverse("oauth:dashboard"))

        return TemplateResponse(request, "oauth:auth", {})

class RegistrationView(View):
    def get(self, request, *args, **kwargs):
        # Ensure the user has verified an email through OAuth
        if not request.session.get("email", False):
            return redirect("login")

        context = {"courses": Course.objects.all()}
        return TemplateResponse(request, "oauth/student_creation.html", context)

class RegistrationCallbackView(View):
    # This should only receive POSTs
    def get(self, request, *args, **kwargs):
        return redirect(reverse("oauth:dashboard"))

    def post(self, request, *args, **kwargs):
        return oauth.register_user(request)


class AuthView(View):
    def get(self, request, *args, **kwargs):
        """Starts the OAuth authorization flow and redirects to Google for login/authorization"""
        redirect_uri=request.build_absolute_uri(reverse('oauth:callback'))
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(settings.OAUTH_CLIENT_SECRET_PATH,
                                                                       scopes=["https://www.googleapis.com/auth/userinfo.email openid"],
                                                                       redirect_uri=redirect_uri)
        authorization_url, state = flow.authorization_url(
            # Allow refreshing an access token without re-prompting the user for permission.
            access_type='offline',
            # Enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true')
        return redirect(authorization_url)

class CallbackView(View):
    def get(self, request, *args, **kwargs):
        next_redirect = handle_oauth_callback(request)
        if next_redirect is None:
            # TODO make this show an invalid login message to the user
            return redirect(reverse("landing:landing_page"))
        return next_redirect

class LandingView(oauth.RequireLoggedInMixin, View):
    # even after going through google oauth, we aren't logged in so we never make it to dsahboard, instead 
    # brings the user back to the landing page (before google oauth)
    def get(self, request):
        return render(request, "oauth/dashboard.html")

