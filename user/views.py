from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, "Passwords do not match")
            return render(request, 'user/signup/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'user/signup/signup.html')

        user = User.objects.create_user(username=username, password=password)

        response = redirect('/')
        response.set_cookie('username', username, max_age=60*60*24*14)
        response.set_cookie('id', user.id, max_age=60*60*24*14)
        return response

    return render(request, 'user/signup/signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user) 
            response = redirect('/')
            response.set_cookie('id', user.id, max_age=60*60*24*14)
            response.set_cookie('username', username, max_age=60*60*24*14)
            return response
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'user/login/login.html')
