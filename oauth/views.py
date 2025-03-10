from django.views import View
from django.http.response import HttpResponse
from django.views.generic.base import TemplateView
import google.oauth2.credentials
import google_auth_oauthlib.flow
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from . import oauth
from django.http.response import JsonResponse

class LoginView(TemplateView):
    template_name = "login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class AuthView(View):
    def get(self, request, *args, **kwargs):
        """Starts the OAuth authorization flow and redirects to Google for login/authorization"""
        redirect_uri=request.build_absolute_uri(reverse('callback'))
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
        credentials = oauth.get_credentials(request)
        if credentials == None:
            # TODO make this show an invalid login attempt message to the user
            return redirect(reverse("login"))

        email = oauth.get_email(credentials)
        if oauth.verify_email(email):
            return JsonResponse({'token': credentials.token,
                                     'refresh_token': credentials.refresh_token,
                                     'token_uri': credentials.token_uri,
                                     'client_id': credentials.client_id,
                                     'client_secret': credentials.client_secret,
                                     'granted_scopes': credentials.granted_scopes})
        else:
            # TODO make this show an invalid account message to the user
            return redirect(reverse("login"))
