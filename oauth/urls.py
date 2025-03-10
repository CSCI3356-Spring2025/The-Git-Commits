from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name="login"),
    path('auth/', views.AuthView.as_view(), name="auth"),
    path('callback/', views.CallbackView.as_view(), name="callback"),
]

