from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from eventapp.models import User
from functools import wraps
from django.http import JsonResponse
from .forms import BookingComedyShowForm
import json
from django.core.mail import send_mail
from django.contrib.auth import login as auth_login, logout as auth_logout
import random
from django.urls import reverse
from django. db import transaction
from .models import Event,Movie,ComedyShow,AmusementPark,LiveConcert,MovieScreen,TheaterSeat,TicketBooking,LiveConcertTicketBooking,AmusementTicket,BookingsEvent
from django.contrib.admin.views.decorators import staff_member_required


def login_required_session(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        print(f"Session data: {dict(request.session)}")  # Debug line
        print(f"User authenticated: {request.session.get('user_authenticated')}")  # Debug line
        
        if not request.session.get('user_authenticated'):
            messages.error(request, 'Please login to access this page')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required_session
def home(request):
    events = Event.objects.all()
    movies = Movie.objects.all()
    comedyshows = ComedyShow.objects.all()
    amusements = AmusementPark.objects.all()
    liveconcerts = LiveConcert.objects.all()
    messages.success(request,"Succesfully Login!")
    return render(request,"home.html",{
        'events':events,
        'movies':movies,
        'comedyshows':comedyshows,
        'amusements':amusements,
        'liveconcerts':liveconcerts,
    })

def signup(request):
    if request.method == "POST":
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')   
        mobile = request.POST.get('mobile')   
        password = request.POST.get('password')   
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request,'Passwords do not match!')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request,"Email already registered")
            return redirect('signup')
        
        if User.objects.filter(mobile=mobile).exists():
            messages.error(request,"Mobile number already registered")
            return redirect('signup')
        
        User.objects.create(
            firstname = firstname,
            lastname = lastname,
            email = email,
            mobile = mobile,
            password = password,
        )

        messages.success(request,"registration success! Please log in")
        return redirect('login')
    return render(request,'signup.html')

def login(request):
    if request.method == "POST":
        user_input = request.POST.get('user_input')
        user=None
        email_to_send=None

        if '@' in user_input:
            try:
                user = User.objects.get(email=user_input)
                email_to_send=user.email
            except User.DoesNotExist:
                messages.error(request,'Email not registered')
                return redirect('login')
        
        else:
            try:
                user = User.objects.get(mobile=user_input)
                email_to_send = user.email
            except User.DoesNotExist:
                messages.error(request,"Mobile not registered")
                return redirect("login")
            
        otp = random.randint(100000,999999)
        request.session["otp"] = otp
        request.session["user_id"] = user.id

         # Professional email format
        email_subject = "Your EventHub Login OTP"
        email_message = f"""
        
Dear {user.firstname},

You have initiated a login request for your EventHub account. To ensure the security of your account, we require verification using the One-Time Password provided below.

SECURITY VERIFICATION CODE: {otp}

This verification code is valid for 10 minutes from the time of this request and may be used only once.

For your security:
• Do not share this code with anyone
• EventHub representatives will never ask for this code
• This code is required only for login authentication

If you did not initiate this login attempt, please secure your account immediately by:
1. Changing your account password
2. Contacting our Security Team at security@eventhub.com
3. Reviewing recent account activity

Thank you for choosing EventHub as your entertainment partner.

Sincerely,
EventHub Security Team

Customer Support: +91-XXXXX-XXXXX
Website: www.eventhub.com
Email: support@eventhub.com

---
This is an automated security message. Please do not reply to this email.
For security reasons, we recommend deleting this email after use."""

        send_mail(
            subject=email_subject,
            message=email_message,
            from_email="EventHub <marati.nikhil9@gmail.com>",
            recipient_list=[email_to_send],
            fail_silently=False
        )

        messages.success(request,"OTP sent to your email")

        return redirect("login_otp_verify")
    
    return render(request,"login.html")


def login_otp_verify(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        if str(request.session.get('otp')) == entered_otp:
            return redirect("login_password")
        else:
            messages.error(request,"Invalid OTP!")
            return redirect("login_otp_verify")
    # messages.success(request,'Please enter your OTP')
    return render(request,"login_otp_verify.html")


def login_password(request):
    if request.method == "POST":
        password = request.POST.get("password")
        user = User.objects.get(id=request.session["user_id"])

        if user.password == password:
            request.session['user_authenticated'] = True
            request.session['user_name'] = user.firstname
            # messages.error(request, f"Welcome {user.firstname}")
            request.session.modified = True
            return redirect("home")
        else:
            messages.error(request,"Incorrect password!")
            return redirect("login_password")
    else:
        messages.success(request,'Please Enter your password')
    # messages.success(request,"Succesfully Login!")
    return render(request,"login_password.html")


def logout(request):
    request.session.flush()
    return redirect('login')


@login_required_session
def events(request):
    events = Event.objects.all()
    return render(request,'events.html',{'events':events})


@login_required_session
def event_view(request,id):
    event = get_object_or_404(Event, id=id)
    return render(request,'event_view.html',{"event":event})


def event_book_tickets(request,business_event_id):
    event = get_object_or_404(Event,pk=business_event_id)
    
    if event.is_sold_out:
        return render(request,"bookings/event_booktickets.html",{"event":event})
    
    if request.method == "POST":
        customer_name = request.POST.get("customer_name","").strip()
        customer_email = request.POST.get("customer_email","").strip()
        customer_phone = request.POST.get("customer_phone","").strip()
        special_request = request.POST.get("special_request","").strip()

        number_of_tickets = int(request.POST.get('number_of_tickets',1))

        if number_of_tickets > event.available_seats:
            messages.error(
                request,
                f"Only {event.available_seats} seats available! Please reduce ticket quantity"
            )
            return redirect(reverse("event_book_tickets",args = [event.id]))
        
        total_amount = event.ticket_price  * number_of_tickets

        try:
            with transaction.atomic():
                booking = BookingsEvent.objects.create(
                    event = event,
                    user = request.user if request.user.is_authenticated else None,
                    number_of_tickets = number_of_tickets,
                    total_amount = total_amount,
                    status = "Confirmed",
                    customer_name = customer_name,
                    customer_email = customer_email,
                    customer_phone = customer_phone,
                    special_request = special_request,
                    payment_status = False,
                )

                event.update_available_seats()

                messages.success(request,f"Booking successful! Your booking ID is {booking.booking_id}")

                return redirect(reverse("booking_success",args=[booking.booking_id]))
        except Exception as e:
            print("Error:",e)
            messages.error(request,"Something went wrong while processing your booking")
            return redirect(reverse("event_book_tickets",args=[event.id]))
        
    return render(request,"book_tickets/events_booktickets.html",{"event":event})
        


@login_required_session
def movies(request):
    movies = Movie.objects.all()
    return render(request,'movies.html',{'movies':movies})

@login_required_session
def movie_view(request,id):
    movie = get_object_or_404(Movie, id=id)
    return render(request,'movie_view.html',{"movie":movie})


@login_required_session
def amusements(request):
    amusement = AmusementPark.objects.all()
    return render(request,'amusements.html',{'amusement':amusement})


@login_required_session
def amusements_view(request, id):
    amusement = get_object_or_404(AmusementPark, id=id)
    return render(request, 'amusements_view.html', {'amusement': amusement})


def get_park_tickets(request, park_id):
    try:
        park = AmusementPark.objects.get(id=park_id)
        tickets = AmusementTicket.objects.filter(amusement_park_id=park_id)
        ticket_data = []       
        for ticket in tickets:
            ticket_data.append({
                'id': ticket.id, 
                'name': f"{ticket.get_category_display()} - {ticket.get_sub_category_display()}"
            })
            
        return JsonResponse({'success': True, 'tickets': ticket_data, 'park_name': park.park_name})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
  

def get_ticket_details(request, ticket_id):
    try:
        ticket = AmusementTicket.objects.get(id=ticket_id)
        return JsonResponse({
            'success': True,
            'base_price': str(ticket.base_price),
            'discount_percent': ticket.discount_percent,
            'gst_percent': str(ticket.gst_percent)
        })
    except AmusementTicket.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Ticket not found'})


def get_park_price(request, park_id):
    try:
        park = AmusementPark.objects.get(id=park_id)
        return JsonResponse({'success': True, 'ticket_price': str(park.ticket_price),'park_name': park.park_name})
    except AmusementPark.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Park not found'})


def amusements_book_tickets(request,park_id):
    park = get_object_or_404(AmusementPark,id=park_id)
    is_wonderla = park.park_name.lower().startswith('wonderla')

    context = {
        'park':park,
        'is_wonderla':is_wonderla,
        'available_tickets':park.tickets.all() if is_wonderla else [],
    }

    return render(request,'book_tickets/amusements_booktickets.html',context)

@login_required_session
def liveconcerts(request):
    liveconcert = LiveConcert.objects.all().order_by('-date')
    return render(request,'liveconcerts.html',{'liveconcert':liveconcert})

@login_required_session
def liveconcerts_view(request,id):
    show = get_object_or_404(LiveConcert, id=id)
    return render(request,'liveconcerts_view.html',{'show':show})

@login_required_session
def liveconcerts_book_ticket(request,concert_id):
    concert = get_object_or_404(LiveConcert, id=concert_id)
    if request.method == "POST":
        ticket_type = request.POST.get('ticket_type')
        quantity = int(request.POST.get('quantity',1))

        if quantity > concert.available_seats:
            messages.error(request,'Not enough seats available')
            return redirect('liveconcerts_view.html',id=concert_id)
        
        booking = LiveConcertTicketBooking.objects.create(
            user = request.user,
            concert = concert,
            ticket_type = ticket_type,
            quantity = quantity,
        )

        messages.success(request,'Ticket booked successfully!')
        return redirect('ticket_success',booking_id = booking.id)
    
    return render(request,'book_tickets/liveconcerts_bookticket.html',{'concert':concert})

@login_required_session
def ticket_success(request,booking_id):
    booking = get_object_or_404(LiveConcertTicketBooking,id=booking_id)
    return render(request,'ticket_success.html',{'booking':booking})

@login_required_session
def comedyshows(request):
    comedyshows = ComedyShow.objects.all()
    return render(request,'comedyshows.html',{"comedyshows":comedyshows})


@login_required_session
def comedyshows_view(request,id):
    comedyshow = get_object_or_404(ComedyShow, id=id)
    return render(request,'comedyshows_view.html',{"comedyshow":comedyshow})


@login_required_session
def book_comedy_tickets(request,pk):
    comedy_show = get_object_or_404(ComedyShow,pk=pk)
    if request.method == "POST":
        form = BookingComedyShowForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.comedy_show = comedy_show
            booking.total_price = booking.number_of_tickets * comedy_show.ticket_price
            booking.save()
            return redirect('booking_success')
    else:
        form = BookingComedyShowForm()
    return render(request, 'book_tickets/comedy_show_book_tickets.html',{
        "comedy_show":comedy_show,
        "form":form
    })

@login_required_session
def contactus(request):
    return render(request,'contactus.html')

@login_required_session
def aboutus(request):
    return render(request,'aboutus.html')

@login_required_session
def helpcenter(request):
    return render(request,'helpcenter.html')

@login_required_session
def privacy_policy(request):
    return render(request,'privacy&policy.html')


@login_required_session
def termsandconditions(request):
    return render(request,'terms&conditions.html')


@login_required_session
def refundpolicy(request):
    return render(request,'refundpolicy.html')


@login_required_session
def book_movie_tickets(request, movie_id):
    movie = get_object_or_404(Movie, id = movie_id)
    screens = movie.screens.all()

    selected_screen_id = request.GET.get('screen')
    selected_screen = None

    if selected_screen_id:
        selected_screen_id = get_object_or_404(MovieScreen, id=selected_screen_id, movie = movie)
    else:
        selected_screen = screens.first() if screens else None

    seat_config = {}
    for screen in screens:
        seats = TheaterSeat.objects.filter(screen = screen).order_by('row','number')
        seat_config[screen.id] = {
            'premium':seats.filter(seat_type = 'premium'),
            'executive':seats.filter(seat_type = 'executive'),
            'normal':seats.filter(seat_type = 'normal'),
        }

    if request.method == "POST":
        screen_id = request.POST.get('screen')
        selected_seats = request.POST.getlist('seats')

        if not screen_id or not selected_seats:
            return render(request,'book_tickets/movies_booktickets.html',{
                'movie':movie,
                'screens':screens,
                'selected_screen':selected_screen,
                'seat_config':seat_config,
                'error':'Please select a screen and at least one seat'
            })
        
        screen = get_object_or_404(MovieScreen, id = screen_id)
        seats_qs = TheaterSeat.objects.filter(screen = screen, id__in = selected_seats)
        booked_seats = seats_qs.filter(status = "Booked")
        
        if booked_seats.exists():
            return render(request,'book_tickets/movies_booktickets.html',{
                'movie':movie,
                'screens':screens,
                'selected_screen':selected_screen,
                'seat_config':seat_config,
                'error': 'Some selected seats are already booked. please select again'
            })
        
        booking = TicketBooking.objects.create(
            user = request.user,
            movie = movie,
            screen = screen
        )

        booking.seats.set(seats_qs)
        booking.save()

        return redirect('booking_success',booking_id = booking.id)
    
    return render(request,'book_tickets/movies_booktickets.html',{
        'movie':movie,
        'screens':screens,
        'selected_screen':selected_screen,
        'seat_config':seat_config,
    })


def get_screen_seats(request, screen_id):
    try:
        screen = MovieScreen.objects.get(id = screen_id)

        seats = []
        total_rows = screen.total_rows or 10
        seats_per_row = screen.seats_per_row or 12

        for row in range(1, total_rows + 1):
            for seat_num in range(1, seats_per_row + 1):
                seat_id = f"{row}_{seat_num}"
                seats.append({
                    "id":seat_id,
                    "row":row,
                    "number":seat_num,
                    "status":"Available",
                    "section": "Premium" if row <= 3 else "executive" if row <= 6 else "normal"

                })

        return JsonResponse({'seats':seats})
    except MovieScreen.DoesNotExist:
        return JsonResponse({'error':'Screen not found'}, status=404)
    

