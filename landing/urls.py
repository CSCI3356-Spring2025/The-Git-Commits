from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('login/', views.login_page, name='login_page'),
    path('account-type/', views.account_type, name='account_type'),
    path('dashboard/', views.dashboard, name='dashboard'),
]