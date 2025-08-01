from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = "oauth"

urlpatterns = [
    path('auth/', views.AuthView.as_view(), name="auth"),
    path('callback/', views.CallbackView.as_view(), name="callback"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('registration/', views.RegistrationView.as_view(), name="registration"),
    path('registration_callback/', views.RegistrationCallbackView.as_view(), name="registration_callback"),
]

