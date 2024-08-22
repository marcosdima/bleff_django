from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse

from .forms import SignUpForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                return redirect(reverse('game:index'))
            
    form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form, 'label': 'Login'})


def logout_view(request):
    if request.user:
        logout(request)
    
    return redirect('users:login')


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('game:index')
    else:
        form = SignUpForm()
    return render(request, 'users/login.html', {'form': form, 'label': 'Sign Up'})
