from django.shortcuts import render

def landing_page(request):
    return render(request, 'landing/landing_page.html')

def login_page(request):
    return render(request, 'landing/login_page.html')

def account_type(request):
    return render(request, 'landing/account_type.html')

def dashboard(request):
    context = {
        'username': 'TestUser',
        'user_type': 'Professor',
    }
    return render(request, 'landing/dashboard.html', context)