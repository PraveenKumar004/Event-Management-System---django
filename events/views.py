from django.shortcuts import render,redirect, get_object_or_404
from django.http import JsonResponse
import json
from .models import Event,EventRegistration
from django.contrib.auth.models import User

def dashboard(request):
    return render(request, 'events/dashboard/index.html')

def myevents(request):
    user= request.COOKIES.get('id')
    if not user:
        return redirect('/login')
    
    events = Event.objects.filter(user_id=user)

    return render(request, 'events/myevents/index.html', {'events': events})


def registerevents(request):
    user= request.COOKIES.get('id')
    if not user:
        return redirect('/login')

    registrations = EventRegistration.objects.filter(user_id=user)
    events = [registration.event for registration in registrations]
    
    return render(request, 'events/registeredEvents/index.html', {'events': events})


def viewevent(request, event_id):
    user= request.COOKIES.get('id')
    if not user:
        return redirect('/login')

    event = get_object_or_404(Event, id=event_id)   
    registrations = EventRegistration.objects.filter(event=event_id)

    for registration in registrations:
        registration.user = User.objects.get(id=registration.user_id)
  
    context = {
        'event': event,
        'registrations': registrations,
    }
    
    return render(request, 'events/viewEvent/event.html', context)


def annoncewinner(request):
    user= request.COOKIES.get('id')
    if not user:
        return redirect('/login')

    return render(request, 'events/annoncewinner/annoncewinner.html')


def create_event(request):
    user = request.COOKIES.get('id')
    if not user:
        return redirect('/login')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        full_details = request.POST.get('full_details')
        date = request.POST.get('date')
        location = request.POST.get('location')
        total_tickets = request.POST.get('total_tickets')
        poster = request.FILES.get('poster')
        body_unicode = request.POST.get('questions')
        questions_data = json.loads(body_unicode) if body_unicode else []

        event = Event(
            name=name,
            description=description,
            full_details=full_details,
            poster=poster,
            date=date,
            location=location,
            total_tickets=total_tickets,
            questions=questions_data,
            user_id = user
        )
        event.save()

        return JsonResponse({'status': 'success', 'event_id': event.id})

    return render(request, 'events/addevents/addevent.html')



def delete_event(request, event_id):
    if request.method == 'DELETE':
        event = get_object_or_404(Event, id=event_id)
        event.delete()
        return JsonResponse({'success': True}, status=204)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def edit_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':

        event.name = request.POST.get('name', event.name)
        event.description = request.POST.get('description', event.description)
        event.full_details = request.POST.get('full_details', event.full_details)
        event.date = request.POST.get('date', event.date)
        event.location = request.POST.get('location', event.location)
        event.total_tickets = request.POST.get('total_tickets', event.total_tickets)

        poster = request.FILES.get('poster')
        if poster:
            event.poster = poster

        body_unicode = request.POST.get('questions')
        questions_data = json.loads(body_unicode) if body_unicode else []

        event.questions = questions_data

        event.save() 
        return JsonResponse({'status': 'success', 'event_id': event.id})

    return render(request, 'events/editevents/editevent.html', {'event': event})