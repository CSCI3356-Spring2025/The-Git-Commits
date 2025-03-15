import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from django.conf import settings
from django.urls import reverse
from .models import User

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

def get_role(email:str) -> str:
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

    user, created = User.objects.update_or_create(
        email=email,
        defaults={"role": role}
        )

    return user