from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from eventapp.models import User
from functools import wraps
from django.http import JsonResponse
from .forms import BookingComedyShowForm
import json
from django.core.mail import send_mail
from django.contrib.auth import login as auth_login, logout as auth_logout
import random,datetime
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
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
        user = None
        email_to_send = None

        if '@' in user_input:
            try:
                user = User.objects.get(email=user_input)
                email_to_send = user.email
            except User.DoesNotExist:
                messages.error(request, 'Email not registered')
                return redirect('login')
        
        else:
            try:
                user = User.objects.get(mobile=user_input)
                email_to_send = user.email
            except User.DoesNotExist:
                messages.error(request, "Mobile not registered")
                return redirect("login")
            
        otp = random.randint(100000, 999999)
        request.session["otp"] = otp
        request.session["user_id"] = user.id

        # Professional email format
        email_subject = "🔐 Your EventHub Login Verification Code"
        
        # HTML Email Template with styling
        email_html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EventHub Security Verification</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .email-container {{
            background-color: #ffffff;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            border: 1px solid #e0e0e0;
        }}
        .header {{
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
            margin-bottom: 30px;
        }}
        .logo {{
            font-size: 28px;
            font-weight: bold;
            color: #2563eb;
            margin-bottom: 10px;
        }}
        .tagline {{
            color: #64748b;
            font-size: 14px;
        }}
        .otp-container {{
            background: linear-gradient(135deg, #2563eb, #3b82f6);
            color: white;
            padding: 25px;
            border-radius: 8px;
            text-align: center;
            margin: 30px 0;
            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
        }}
        .otp-code {{
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 8px;
            margin: 15px 0;
            font-family: monospace;
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 5px;
            display: inline-block;
        }}
        .otp-expiry {{
            font-size: 14px;
            opacity: 0.9;
            margin-top: 10px;
        }}
        .security-section {{
            background-color: #f8fafc;
            border-left: 4px solid #ef4444;
            padding: 15px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        .security-title {{
            color: #ef4444;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .info-box {{
            background-color: #e8f4fd;
            border-left: 4px solid #2563eb;
            padding: 15px;
            margin: 25px 0;
            border-radius: 4px;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #64748b;
            font-size: 12px;
        }}
        .footer-links {{
            margin: 15px 0;
        }}
        .footer-links a {{
            color: #2563eb;
            text-decoration: none;
            margin: 0 10px;
        }}
        .highlight {{
            color: #2563eb;
            font-weight: bold;
        }}
        .step {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 15px;
        }}
        .step-number {{
            background-color: #2563eb;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 10px;
            font-size: 14px;
            flex-shrink: 0;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <div class="logo">🎭 EventHub</div>
            <div class="tagline">Your Gateway to Unforgettable Experiences</div>
        </div>

        <p>Dear <span class="highlight">{user.firstname if user.firstname else user.email.split('@')[0]}</span>,</p>
        
        <p>You have initiated a login request for your EventHub account. To ensure the security of your account, we require verification using the One-Time Password provided below.</p>
        
        <div class="otp-container">
            <h3 style="margin: 0 0 15px 0; font-size: 18px;">🔒 SECURITY VERIFICATION CODE</h3>
            <div class="otp-code">{otp}</div>
            <div class="otp-expiry">⏰ Valid for 10 minutes | One-time use only</div>
        </div>

        <div class="security-section">
            <div class="security-title">⚠️ SECURITY ADVISORY</div>
            <p>For your protection:</p>
            <div class="step">
                <div class="step-number">1</div>
                <span><strong>Do not share</strong> this code with anyone</span>
            </div>
            <div class="step">
                <div class="step-number">2</div>
                <span>EventHub representatives will <strong>never ask</strong> for this code</span>
            </div>
            <div class="step">
                <div class="step-number">3</div>
                <span>This code is required <strong>only for login authentication</strong></span>
            </div>
        </div>

        <div class="info-box">
            <p><strong>If you did NOT initiate this login attempt:</strong></p>
            <div class="step">
                <div class="step-number">1</div>
                <span>Change your account password immediately</span>
            </div>
            <div class="step">
                <div class="step-number">2</div>
                <span>Contact our Security Team at <span class="highlight">security@eventhub.com</span></span>
            </div>
            <div class="step">
                <div class="step-number">3</div>
                <span>Review recent account activity from your dashboard</span>
            </div>
        </div>

        <p>Thank you for choosing EventHub as your entertainment partner.</p>
        <p style="margin-bottom: 30px;">
            Sincerely,<br>
            <strong>EventHub Security Team</strong>
        </p>

        <div class="footer">
            <div class="footer-links">
                <a href="https://www.eventhub.com/help">Help Center</a> | 
                <a href="https://www.eventhub.com/privacy">Privacy Policy</a> | 
                <a href="https://www.eventhub.com/terms">Terms of Service</a>
            </div>
            <div>
                <strong>Customer Support:</strong> +91-98765-43210<br>
                <strong>Website:</strong> <a href="https://www.eventhub.com">www.eventhub.com</a><br>
                <strong>Email:</strong> support@eventhub.com
            </div>
            <div style="margin-top: 20px; color: #94a3b8;">
                <em>This is an automated security message. Please do not reply to this email.<br>
                For security reasons, we recommend deleting this email after successful login.</em>
            </div>
        </div>
    </div>
</body>
</html>
"""

        # Plain text version as fallback
      

        # Send email with HTML content
        try:
            # First, send the HTML email
            from django.core.mail import EmailMultiAlternatives
            
            email = EmailMultiAlternatives(
                subject=email_subject,
                from_email="EventHub Security <security@eventhub.com>",
                to=[email_to_send],
                reply_to=["no-reply@eventhub.com"]
            )
            
            # Attach HTML version
            email.attach_alternative(email_html_message, "text/html")
            
            # Send email
            email.send(fail_silently=False)
            
            messages.success(request, "✅ OTP has been sent to your registered email address")
            
            # Log the OTP sending activity (optional)
            print(f"OTP {otp} sent to {email_to_send} for user {user.id}")
            
        except Exception as e:
            messages.error(request, "Failed to send OTP. Please try again.")
            print(f"Email sending error: {e}")
            return redirect("login")

        return redirect("login_otp_verify")
    
    return render(request, "login.html")

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
        if 'forgot_password' in request.POST:
            email = request.POST.get('email')
            return redirect('forgot_password')
        
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


def forgot_password(request):
    """Step 1: User enters email, we send reset link"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate reset token
            reset_token = user.generate_reset_token()
            
            # Build reset URL
            reset_url = f"{request.scheme}://{request.get_host()}/reset-password/{reset_token}/"
            
            # Prepare email content
            subject = 'Password Reset Request'
            html_message = render_to_string('email/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
                'expiry_hours': 24,
            })
            plain_message = strip_tags(html_message)
            
            # Send email
            try:
                send_mail(
                    subject=subject,
                    message=plain_message,
                    html_message=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                
                messages.success(request, f'Password reset link has been sent to {email}. Please check your inbox.')
                return render(request, 'forgot_password.html')
                
            except Exception as e:
                # If email fails, show the link for testing
                messages.warning(request, f'Email sending failed. Here is your reset link: {reset_url}')
                messages.info(request, 'For testing, you can use this link directly.')
                return render(request, 'forgot_password.html')
            
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            messages.success(request, 'If your email exists in our system, you will receive a reset link shortly.')
            return render(request, 'forgot_password.html')
    
    return render(request, 'forgot_password.html')


def reset_password(request, token):
    """Step 2: User clicks reset link and sets new password"""
    try:
        # Find user with valid reset token
        user = User.objects.get(reset_token=token)
        
        # Check if token is valid
        if not user.is_reset_token_valid():
            messages.error(request, 'Reset link has expired. Please request a new one.')
            user.clear_reset_token()  # Clear expired token
            return redirect('forgot_password')
        
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # Validate passwords
            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'reset_password.html')
            
            # Check password strength
            if len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
                return render(request, 'reset_password.html')
            
            # Update user password
            user.password = new_password
            user.clear_reset_token()  # Clear token after successful reset
            
            # Send confirmation email
            try:
                send_mail(
                    subject='Password Reset Successful',
                    message=f'Your password has been successfully reset. If you did not make this change, please contact support immediately.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except:
                pass  # Ignore email errors for confirmation
            
            messages.success(request, 'Password reset successful! You can now login with your new password.')
            return redirect('login')
        
        # GET request - show reset form
        return render(request, 'reset_password.html', {'token': token})
        
    except User.DoesNotExist:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('forgot_password')


def logout(request):
    request.session.flush()
    return redirect('login')

def profile(request):
    """
    Display and update user profile information
    """
    if not request.session.get('user_authenticated'):
        messages.error(request, 'Please login to access your profile')
        return redirect('login')
    
    # Get user from database using session email
    user_email = request.session.get('user_email')
    try:
        user = User.objects.get(email=user_email)
        
        # Prepare user data for template
        user_data = {
            'id': user.id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'fullname': f"{user.firstname} {user.lastname}",
            'email': user.email,
            'mobile': user.mobile,
            # Add any additional fields you might have
            'joined_date': user.created_at.strftime('%Y-%m-%d') if hasattr(user, 'created_at') else '2024-01-01',
        }
        
    except User.DoesNotExist:
        # Fallback to session data if user not found
        user_data = {
            'firstname': request.session.get('user_name', 'User').split()[0] if ' ' in request.session.get('user_name', 'User') else request.session.get('user_name', 'User'),
            'lastname': request.session.get('user_name', 'User').split()[1] if ' ' in request.session.get('user_name', 'User') and len(request.session.get('user_name', 'User').split()) > 1 else '',
            'fullname': request.session.get('user_name', 'User'),
            'email': request.session.get('user_email', 'user@example.com'),
            'mobile': request.session.get('user_phone', 'Not provided'),
            'joined_date': request.session.get('joined_date', '2024-01-01'),
        }
    
    context = {
        'user': user_data,
    }
    
    return render(request, 'profile.html', context)

def update_profile(request):
    """
    Handle profile update via AJAX
    """
    if not request.session.get('user_authenticated'):
        return JsonResponse({'success': False, 'message': 'Authentication required'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_email = request.session.get('user_email')
            
            try:
                user = User.objects.get(email=user_email)
                
                # Update user fields
                user.firstname = data.get('firstname', user.firstname)
                user.lastname = data.get('lastname', user.lastname)
                user.email = data.get('email', user.email)
                user.mobile = data.get('mobile', user.mobile)
                user.save()
                
                # Update session data
                request.session['user_name'] = f"{user.firstname} {user.lastname}"
                request.session['user_email'] = user.email
                request.session['user_phone'] = user.mobile
                request.session.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Profile updated successfully',
                    'user': {
                        'fullname': f"{user.firstname} {user.lastname}",
                        'firstname': user.firstname,
                        'lastname': user.lastname,
                        'email': user.email,
                        'mobile': user.mobile,
                    }
                })
                
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found'})
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid data format'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

def change_password(request):
    """
    Handle password change
    """
    if not request.session.get('user_authenticated'):
        return JsonResponse({'success': False, 'message': 'Authentication required'})
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            current_password = data.get('current_password')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')
            user_email = request.session.get('user_email')
            
            # Validate passwords
            if not current_password or not new_password or not confirm_password:
                return JsonResponse({'success': False, 'message': 'All fields are required'})
            
            if new_password != confirm_password:
                return JsonResponse({'success': False, 'message': 'New passwords do not match'})
            
            if len(new_password) < 6:
                return JsonResponse({'success': False, 'message': 'Password must be at least 6 characters'})
            
            try:
                user = User.objects.get(email=user_email)
                
                # Verify current password (plain text comparison since you're storing plain text)
                if user.password != current_password:
                    return JsonResponse({'success': False, 'message': 'Current password is incorrect'})
                
                # Update password
                user.password = new_password
                user.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Password changed successfully'
                })
                
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'User not found'})
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid data format'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# views.py
def settings_view(request):
    accent_colors = [
        {'value': 'blue', 'bg': 'bg-blue-500', 'ring': 'blue'},
        {'value': 'green', 'bg': 'bg-green-500', 'ring': 'green'},
        {'value': 'purple', 'bg': 'bg-purple-500', 'ring': 'purple'},
        {'value': 'pink', 'bg': 'bg-pink-500', 'ring': 'pink'},
        {'value': 'orange', 'bg': 'bg-orange-500', 'ring': 'orange'},
        {'value': 'teal', 'bg': 'bg-teal-500', 'ring': 'teal'},
    ]
    
    return render(request, 'settings.html', {
        'accent_colors': accent_colors,
        'user': request.user,
    })


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
    

