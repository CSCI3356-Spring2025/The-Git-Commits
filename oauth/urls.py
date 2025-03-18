from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('auth/', views.AuthView.as_view(), name="auth"),
    path('callback/', views.CallbackView.as_view(), name="callback"),

    # These should be refactored out of this app later
    path('login/', views.LoginView.as_view(), name="login"),
    path('registration/', views.RegistrationView.as_view(), name="registration"),
    path('registration_callback/', views.RegistrationCallbackView.as_view(), name="registration_callback"),
    path('landing/', views.LandingView.as_view(), name="landing"),
]

