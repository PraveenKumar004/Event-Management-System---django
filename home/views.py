from django.shortcuts import render, get_object_or_404, redirect
from .models import Event,EventRegistration
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
import json
from django.db import IntegrityError

def home(request):
    events = Event.objects.all() 
    return render(request, 'home/home/home.html', {'events': events})

def viewevent(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'home/viewevent/event.html', {'event': event})


def register(request, event_id):

    if 'username' not in request.COOKIES:
        return redirect('/login')

    user_id = request.COOKIES.get('id')  
    
    if EventRegistration.objects.filter(event=event_id, user_id=user_id).exists():
        message = "You are already registered for this event."
        return render(request, 'home/home/alert.html', {'message': message})     
    
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'home/register/register.html', {
        'event': event,
        'user': request.COOKIES['username'],  
    })



def register_event(request, event_id):
    
    user_id = request.COOKIES.get('id')
    event = get_object_or_404(Event, id=event_id)
    answers = []

    if event.total_tickets <= 0:
        message = "No tickets available for this event."
        return render(request, 'home/home/alert.html', {'message': message})
    
    for question in event.questions:
        answer = request.POST.get(f"question_{question['id']}")
        answers.append({
            'id': question['id'],
            'question': question['question'],
            'answer': answer,
        })
    try:
        EventRegistration.objects.create(
            event=event,
            user_id=user_id,
            answers=json.dumps(answers)
        )
        event.total_tickets -= 1
        event.save()
        message = "Successfully registered for the event!"
        return render(request, 'home/home/sucess.html', {'message': message})
    except IntegrityError:
        message = "An error occurred while registering. Please try again."
        return render(request, 'home/home/alert.html', {'message': message})


def winner(request):
    return render(request, 'home/winner/winner.html')




