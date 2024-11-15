from django.shortcuts import render, get_object_or_404, redirect
from .models import Event,EventRegistration
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.core.mail import EmailMessage
import json
from django.db import IntegrityError
import razorpay
from django.conf import settings
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import qrcode
import tempfile


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


def winner(request):
    events = Event.objects.filter(winner__isnull=False)
    event_winner_details = []
    for event in events:
        winner_registration = EventRegistration.objects.filter(event=event, winner=True).first()
        if winner_registration:
            user_id = winner_registration.user_id
            user = User.objects.get(id = user_id)
            print("Username",user.username)
            winner_data = {
                'event': event,
                'winner_user_name': user.username,
                'winner_ticket_id': winner_registration.ticket_id,
                'winner_name': user.first_name,  
                'winner_username': user.username ,
                'email' : user.email
            }
            event_winner_details.append(winner_data)
    return render(request, 'home/winner/winner.html',{'event_winner_details': event_winner_details})


# payment gateway
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

def register_event(request, event_id):
    user_id = request.COOKIES.get('id') 
    event = get_object_or_404(Event, id=event_id)
    answers = []
    if event.total_tickets <= 0:
        message = "No tickets available for this event."
        return render(request, 'home/home/alert.html', {'message': message})
    if (event.questions):
        for question in event.questions:
            if isinstance(question, dict):  
                question_id = question.get('id')
                question_text = question.get('question')
            else:  
                question_id = question.id
                question_text = question.question
    
        answer = request.POST.get(f"question_{question_id}")
        answers.append({
            'id': question_id,
            'question': question_text,
            'answer': answer,
        })

    try:
        if event.amount > 0:
           response = redirect('initiate_payment', event_id=event_id)
           response.set_cookie('registration_data', json.dumps({
            'event_id': event_id,
            'user_id': user_id,
            'answers': answers,
            'participation': False,
            'winner' :False,
            'ticket_id' : f"{event_id}U{user_id}",
            }), path='/')  
           return response 
        
        else:
            EventRegistration.objects.create(
                event=event,
                user_id=user_id,
                answers=json.dumps(answers),
                participation= False,
                ticket_id = f"{event_id}U{user_id}",
                winner =False,
            )
            event.total_tickets -= 1
            event.total_collection += event.amount
            event.save()

            ticket_pdf_content = downloadticket(request, f"{event_id}U{user_id}", event, user_id)
            email = User.objects.get(id=user_id)
            subject = '🎉 Registration Successful - Event Confirmation'
            message = f"""
            Dear Participant 👋,

            We are thrilled to inform you that your registration for the event "{event}" has been successfully completed ✅. 

            Thank you for registering! We can't wait to see you at the event 🥳.

            🎟️ Please find attached your event ticket. You can download and save it for entry to the event 🎫.

            Best regards,  
            The Event Management Team 
            """
            email_message = EmailMessage(
                subject,
                message,
                'praveenkumarv989@gmail.com',  
                [email],  
            )
            email_message.attach(f"ticket_{event_id}U{user_id}.pdf", ticket_pdf_content, 'application/pdf')
            email_message.send(fail_silently=False)

            message = "Successfully registered for the event!"
            return render(request, 'home/home/sucess.html', {'message': message})
    except IntegrityError:
        message = "An error occurred while registering. Please try again."
        return render(request, 'home/home/alert.html', {'message': message})

def initiate_payment(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'home/payment/checkout.html', {
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount': event.amount 
    })

def create_order(request):
    if request.method == "POST":
        amount = int(request.POST.get("amount")) * 100  
        order_data = {
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1  
        }
        order = razorpay_client.order.create(order_data)
        order_id = order['id']

        return render(request, 'home/payment/checkout.html', {
            'order_id': order_id,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': amount/100
        })
    return HttpResponse("Invalid Request")

def payment_success(request):
    if request.method == "POST":
        registration_data = json.loads(request.COOKIES.get('registration_data'))
        event = get_object_or_404(Event, id=registration_data['event_id'])
        EventRegistration.objects.create(
            event=event,
            user_id=registration_data['user_id'],
            answers=json.dumps(registration_data['answers']),
            participation= False,
            ticket_id = registration_data['ticket_id'],
            winner =False,
        )
        event.total_tickets -= 1
        event.total_collection += event.amount
        event.save()
        email = User.objects.get(id=registration_data['user_id'])
        ticket_pdf_content = downloadticket(request, f"{registration_data['event_id']}U{registration_data['user_id']}", event, registration_data['user_id'])
        subject = '🎉 Registration Successful - Event Confirmation'
        message = f"""
        Dear Participant 👋,
        We are thrilled to inform you that your registration for the event "{event}" has been successfully completed ✅. 
        Thank you for registering! We can't wait to see you at the event 🥳.
        🎟️ Please find attached your event ticket. You can download and save it for entry to the event 🎫.
        Best regards,  
        The Event Management Team 
        """
        email_message = EmailMessage(
            subject,
            message,
            'praveenkumarv989@gmail.com',  
            [email],  
        )
        email_message.attach(f"ticket_{registration_data['event_id']}U{registration_data['user_id']}.pdf", ticket_pdf_content, 'application/pdf')
        email_message.send(fail_silently=False)

        response = HttpResponse("Payment successful and registration completed.")
        response.delete_cookie('registration_data')
        return response
    return HttpResponse("Invalid Request")



def downloadticket(request, ticket_id, event, user):
    # Create a unique ticket URL
    user_details_url = f"{ticket_id}"  
    qr = qrcode.make(user_details_url)

    # Create a temporary file to store the QR code
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        qr.save(temp_file, format='PNG')
        qr_path = temp_file.name  

    # Set up ticket size and PDF response
    ticket_size = (612, 200)
    pdf_buffer = BytesIO()
    p = canvas.Canvas(pdf_buffer, pagesize=ticket_size)
    
    # Set background color
    p.setFillColor(colors.HexColor("#3a3a55"))
    p.rect(0, 0, ticket_size[0], ticket_size[1], stroke=0, fill=1)

    # Ticket border
    p.setStrokeColor(colors.white)
    p.setLineWidth(2)
    p.roundRect(10, 10, ticket_size[0] - 20, ticket_size[1] - 20, radius=10, stroke=1, fill=0)

    # Ticket details
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.white)
    p.drawRightString(ticket_size[0] - 40, ticket_size[1] - 40, f"Ticket ID: {ticket_id}")

    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(ticket_size[0] / 2, 160, event.name)

    p.setFont("Helvetica", 12)
    p.drawString(40, 120, f"Event ID: {event.id}")
    p.drawString(40, 100, f"Venue: {event.location}")
    p.drawString(40, 80, f"Date: {event.date.strftime('%d-%m-%Y')}")
    p.drawString(40, 60, f"User ID: {user}")

    # Add QR code to the ticket
    qr_code_x = 480
    qr_code_y = 40
    p.drawImage(qr_path, qr_code_x, qr_code_y, width=80, height=80)

    # Footer text
    p.setFont("Helvetica-Oblique", 12)
    p.drawCentredString(ticket_size[0] / 2, 20, "Thank you for attending our event!")

    # Save the PDF into the buffer
    p.showPage()
    p.save()

    # Get the PDF content as an attachment
    pdf_content = pdf_buffer.getvalue()
    pdf_buffer.close()

    return pdf_content