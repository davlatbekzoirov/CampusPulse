from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import RegisterForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('extracurricular:dashboard')
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Welcome, {user.username}!')
        return redirect('extracurricular:dashboard')
    return render(request, 'accounts/auth.html', {'form': form, 'mode': 'register'})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('extracurricular:dashboard')
    form = AuthenticationForm(request, data=request.POST or None)
    if form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get('next', 'extracurricular:dashboard'))
    return render(request, 'accounts/auth.html', {'form': form, 'mode': 'login'})

def logout_view(request):
    logout(request)
    return redirect('login')