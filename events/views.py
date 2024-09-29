from django.shortcuts import render

def dashboard(request):
    return render(request, 'events/dashboard/index.html')

def myevents(request):
    return render(request, 'events/myevents/index.html')

def registerevents(request):
    return render(request, 'events/registeredEvents/index.html')
