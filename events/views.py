from django.shortcuts import render,redirect, get_object_or_404
import json
import qrcode
import tempfile
from .models import Event,EventRegistration
from django.contrib.auth.models import User
from django.http import HttpResponse,JsonResponse
from reportlab.pdfgen import canvas
from django.utils import timezone
from django.utils.timezone import now
from reportlab.lib import colors
from django.db.models import Sum
from django.contrib import messages
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
from django.conf import settings

def dashboard(request):
    user= request.COOKIES.get('role')
    if (user == 'user'):
        user_id = request.COOKIES.get('id') 
        user_registrations_count = EventRegistration.objects.filter(user_id=user_id).count()
        context = {
            'total_registrations': user_registrations_count,
        }
        return render(request,'events/dashboard/index.html', context)
    elif(user == 'college'):
        user_id = request.COOKIES.get('id')    
        get_events = Event.objects.filter(user_id=user_id)
        events_count = get_events.count() 
        user_registrations_count = EventRegistration.objects.filter(event__in=get_events).count()
        total_collection_sum = get_events.aggregate(Sum('total_collection'))['total_collection__sum'] or 0
        upcoming_event = get_events.filter(date__gt=now()).order_by('date').first()
        winner_event = get_events.filter(date__lt=now()).order_by('-date').first()
        # getupcount = EventRegistration.objects.filter(event_id = upcoming_event.id).count()
        context = {
            'total_events': events_count,
            'total_registrations': user_registrations_count,
            'events': get_events,  
            'collection': total_collection_sum,
            'upevent': upcoming_event,
            'anevent': winner_event,
            
        }
        return render(request, 'events/dashboard/collegeindex.html',context)
    else:
        return redirect('/login')


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


def downloadticket(request, ticket_id):

    user_id = request.COOKIES.get('id')

    event = get_object_or_404(Event, id=ticket_id)
    user = get_object_or_404(User, id=user_id)

    user_details_url = f"{ticket_id}U{user.id}"  

    qr = qrcode.make(user_details_url)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        qr.save(temp_file, format='PNG')
        qr_path = temp_file.name  

    ticket_size = (612, 200)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket_id}.pdf"'

    p = canvas.Canvas(response, pagesize=ticket_size)

    p.setFillColor(colors.HexColor("#3a3a55"))
    p.rect(0, 0, ticket_size[0], ticket_size[1], stroke=0, fill=1)

    p.setStrokeColor(colors.white)
    p.setLineWidth(2)
    p.roundRect(10, 10, ticket_size[0] - 20, ticket_size[1] - 20, radius=10, stroke=1, fill=0)

    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.white)
    p.drawRightString(ticket_size[0] - 40, ticket_size[1] - 40, f"Ticket ID: {ticket_id}U{user.id}")

    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(ticket_size[0] / 2, 160, event.name)

    p.setFont("Helvetica", 12)
    p.drawString(40, 120, f"Event ID: {event.id}")
    p.drawString(40, 100, f"Venue: {event.location}")
    p.drawString(40, 80, f"Date: {event.date.strftime('%d-%m-%Y')}")
    p.drawString(40, 60, f"User: {user.username}")

    qr_code_x = 480
    qr_code_y = 40
    p.drawImage(qr_path, qr_code_x, qr_code_y, width=80, height=80)

    p.setFont("Helvetica-Oblique", 12)
    p.drawCentredString(ticket_size[0] / 2, 20, "Thank you for attending our event!")

    p.showPage()
    p.save()

    return response



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


def winnerselection(request):
    user= request.COOKIES.get('id')
    if not user:
        return redirect('/login')
    current_date = timezone.now().date()
    events = Event.objects.filter(user_id=user, date__lt=current_date, winner="")
    return render(request, 'events/annoncewinner/eventselection.html', {'events': events})

def annoncewinner(request, event_id):
    user = request.COOKIES.get('id')
    if not user:
        return redirect('/login') 
    events = Event.objects.get(id=event_id)
    regis = EventRegistration.objects.filter(event_id=event_id, participation=True)
    userdetails = []
    for registration in regis:
        print(registration.ticket_id)
        user_obj = User.objects.get(id=registration.user_id)
        userdetails.append({
            'first_name': user_obj.first_name,
            'email': user_obj.email,
            'username': user_obj.username,
            'ticket_id':registration.ticket_id
        })

    return render(request, 'events/annoncewinner/annoncewinner.html', {
        'event': events,
        'participation': userdetails,
    })



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
        paid = request.POST.get('paid') == 'true'  
        amount = request.POST.get('amount') if paid else 0

        event = Event(
            name=name,
            description=description,
            full_details=full_details,
            poster=poster,
            date=date,
            location=location,
            total_tickets=total_tickets,
            questions=questions_data,
            user_id = user,
            paid=paid,
            amount=amount,
            total_collection =0,
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

def event_collection(request):

    user_id = request.COOKIES.get('id') 
    user_events = Event.objects.filter(user_id=user_id)
    total_collection_sum = user_events.aggregate(Sum('total_collection'))['total_collection__sum'] or 0

    return render(
        request, 
        'events/accountbalance/account.html', 
        {'user_events': user_events, 'collection': total_collection_sum}
    )

def logout(request):

    response = redirect('/')
    response.delete_cookie('id')
    response.delete_cookie('username')
    response.delete_cookie('role')

    return response

def participation(request):
    user = request.COOKIES.get('id')
    if not user:
        return redirect('/login')

    results = None 
    if 'ticket_id' in request.GET:
        ticket_id = request.GET['ticket_id']
        results = EventRegistration.objects.filter(ticket_id=ticket_id)
        for result in results:
            user = User.objects.get(id =result.user_id )
            

    return render(request, 'events/participation/participation.html', {'results': results,'users':user})

def add_to_event(request, registration_id):
    if request.method == 'POST':
        registration = get_object_or_404(EventRegistration, id=registration_id)
        registration.participation = True
        email = User.objects.get(id=registration.user_id)
        subject = 'Participation Successful - Event Confirmation'
        message = f"""
        Dear Participant,
        We are pleased to inform you that you have successfully participated in the event "{registration.event}". 

        Thank you for your participation! We hope you had a great experience and look forward to your future involvement in our events.
        
        Best regards,
        Event Management Team
        """
        send_mail(
            subject,
            message,
        'praveenkumarv989@gmail.com',
        [email],
        fail_silently=False,
        )
        registration.save()
        messages.success(request, 'Successfully added to event!')
        return redirect('participation')
    return redirect('participation')

def view_registration(request):
    user_id = request.COOKIES.get('id')
    events = Event.objects.filter(user_id=user_id)
    event_ids = events.values_list('id', flat=True)
    registrations = EventRegistration.objects.filter(event_id__in=event_ids).select_related('event')
    userdetails = []
    for registration in registrations:
        user = User.objects.get(id=registration.user_id)
        userdetails.append({
            'first_name': user.first_name,
            'email': user.email,
            'username': user.username
        })
    
    registration_user_pairs = list(zip(registrations, userdetails))
    return render(request, 'events/regiastration/regiastration.html', {'registration_user_pairs': registration_user_pairs})


def announce_winner(request, event_id):
    if request.method == 'POST':
        winner_id = request.POST.get('winners')  
        if winner_id:
            print(f"Winner ID: {winner_id}")

            event = get_object_or_404(Event, id=event_id)
            event.winner = winner_id 

            registrations = EventRegistration.objects.filter(ticket_id=winner_id)

            if registrations.exists():
                reg_id = registrations.first()
                reg_id.winner = True
                reg_id.save()
                event.save()
            return JsonResponse({"status": "success", "message": "Winner announced successfully!"})
        

def profile_view(request):
    user= request.COOKIES.get('role')
    if(user == "college"):
        return profile(request)
    elif(user == "user"):
        return profileuser(request)
    else:
        return redirect('/')

def profile(request):
    user_id = request.COOKIES.get('id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return redirect('login')  
    else:
        return redirect('login') 
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        if 'photo' in request.FILES:
            uploaded_file = request.FILES['photo']
            fs = FileSystemStorage(location=settings.MEDIA_ROOT.joinpath('profile'))
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_url = 'profile/' + filename 
            user.email = file_url
        user.save()
        return redirect('profile')

    return render(request, 'events/profile/profileCollege.html', {'user': user})

def profileuser(request):
    user_id = request.COOKIES.get('id')
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return redirect('login')  
    else:
        return redirect('login') 
    
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        if 'photo' in request.FILES:
            uploaded_file = request.FILES['photo']
            fs = FileSystemStorage(location=settings.MEDIA_ROOT.joinpath('profile'))
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_url = 'profile/' + filename 
            user.email = file_url
        user.save()
        return redirect('profile')

    return render(request, 'events/profile/profile.html', {'user': user})