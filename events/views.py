from django.shortcuts import render
from django.http import JsonResponse
import json

def dashboard(request):
    return render(request, 'events/dashboard/index.html')

def myevents(request):
    return render(request, 'events/myevents/index.html')

def registerevents(request):
    return render(request, 'events/registeredEvents/index.html')

def viewevent(request):
    return render(request, 'events/viewEvent/event.html')

def annoncewinner(request):
    return render(request, 'events/annoncewinner/annoncewinner.html')



def demo(request):
    if request.method == 'POST':
        questions_data = json.loads(request.body)  # Assuming JSON data is sent via JavaScript fetch

        # Collect the received data for testing
        print("Received Questions Data:", questions_data)  # Print data to console for testing

        # Return a success response
        return JsonResponse({"message": "Questions received successfully"}, status=200)

    return render(request, 'events/addevents/addevent.html')

