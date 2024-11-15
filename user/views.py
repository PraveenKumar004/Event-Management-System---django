from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login
from django.utils.timezone import now, timedelta
from .models import OTP
import random

def generate_otp_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')

        otp = str(random.randint(100000, 999999))

        otp_record, created = OTP.objects.get_or_create(username=username)
        otp_record.otp = otp
        otp_record.save() 

        send_mail(
            'Your OTP Code',
            f'Your OTP code is {otp}',
            'praveenkumarv989@gmail.com',
            [username],
            fail_silently=False,
        )

        messages.success(request, "OTP sent successfully and VALID ONLY 2 MINS")
        return render(request,'user/signup/signup.html', {'username':username})
    return redirect('/login/')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        otp_input = request.POST.get('otp')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            messages.error(request, "Passwords do not match")
            return render(request, 'user/signup/signup.html')

        try:
            otp_record = OTP.objects.get(username=username, otp=otp_input)
        except OTP.DoesNotExist:
            messages.error(request, "Invalid OTP")
            return render(request, 'user/signup/signup.html')

        user = User.objects.create_user(username=username, password=password)
        otp_record.delete()  

        group = Group.objects.get(name='user')
        user.groups.add(group)

        response = redirect('/')
        response.set_cookie('role', 'user', max_age=60 * 60 * 24 * 14)
        response.set_cookie('username', username, max_age=60 * 60 * 24 * 14)
        response.set_cookie('id', user.id, max_age=60 * 60 * 24 * 14)

        return response

    return render(request, 'user/signup/signup.html')


def collegesignup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        otp_input = request.POST.get('otp')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, "Passwords do not match")
            return render(request, 'user/signup/signupCollege.html')
        
        print(f"Username: {username}, OTP Input: {otp_input}")
        try:
            otp_record = OTP.objects.get(username=username, otp=otp_input)
        except OTP.DoesNotExist:
            messages.error(request, "Invalid OTP")
            return render(request, 'user/signup/signupCollege.html')

        user = User.objects.create_user(username=username, password=password)
        otp_record.delete()  

        group = Group.objects.get(name='college')
        user.groups.add(group)

        response = redirect('/')
        response.set_cookie('role', 'college', max_age=60*60*24*14)
        response.set_cookie('username', username, max_age=60*60*24*14)
        response.set_cookie('id', user.id, max_age=60*60*24*14)
        
        return response

    return render(request, 'user/signup/signupCollege.html')




def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            response = redirect('/')

            if user.groups.filter(name='college').exists():
                role = 'college'
            else:
                role = 'user'

            response.set_cookie('role', role, max_age=60*60*24*14)
            response.set_cookie('id', user.id, max_age=60*60*24*14)
            response.set_cookie('username', username, max_age=60*60*24*14)
            return response
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'user/login/login.html')
