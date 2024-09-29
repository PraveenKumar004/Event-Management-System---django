from django.shortcuts import render

def home(request):
    return render(request, 'home/home/home.html')

def winner(request):
    return render(request, 'home/winner/winner.html')

def register(request):
    return render(request, 'home/register/register.html')
