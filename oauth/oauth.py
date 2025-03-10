import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from django.conf import settings
from django.urls import reverse

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
