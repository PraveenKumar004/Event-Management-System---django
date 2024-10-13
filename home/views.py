from django.shortcuts import render, get_object_or_404, redirect
from .models import Event

def home(request):
    events = Event.objects.all() 
    return render(request, 'home/home/home.html', {'events': events})

def winner(request):
    return render(request, 'home/winner/winner.html')

def register(request, event_id):
    event = Event.objects.get(id=event_id)
    return render(request, 'home/register/register.html', {'event': event})

def register(request, event_id):

    if 'username' not in request.COOKIES:
        return redirect('/login')  
    
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'home/register/register.html', {
        'event': event,
        'user': request.COOKIES['username'],  
    })


def viewevent(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'home/viewevent/event.html', {'event': event})




