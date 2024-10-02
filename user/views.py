from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User

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

        user = User(username=username, password=password)
        user.save()

        response = redirect('/')  
        response.set_cookie('id', user.id, max_age=60*60*24*14) 
        return response
    
    return render(request, 'user/signup/signup.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)

            if user.password == password:  
                response = redirect('/')
                response.set_cookie('id', user.id, max_age=60*60*24*14)  
                response.set_cookie('username', username, max_age=60*60*24*14)  
                return response
            else:
                messages.error(request, "Incorrect password")
        except User.DoesNotExist:
            messages.error(request, "Username does not exist")

    return render(request, 'user/login/login.html')



