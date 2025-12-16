"""
URL configuration for eventproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from eventapp import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    #Authentication URLs 
    path('', views.login,name="login"),
    path('signup/', views.signup,name="signup"),
    path('logout/', views.logout,name="logout"),
    path('login/otp/', views.login_otp_verify,name="login_otp_verify"),
    # path('resend-otp/', views.resend_otp,name="resend_otp"),
    path('login/password/', views.login_password,name="login_password"),
    
    # Protected URLs 
    path('home/', views.home, name="home"),
    path('events/', views.events, name="events"),
    path('comedyshows/', views.comedyshows, name="comedyshows"),
    path('liveconcerts/', views.liveconcerts, name="liveconcerts"),
    path('movies/', views.movies, name="movies"),
    path('amusements/', views.amusements, name="amusements"),

    path('movies/<int:id>', views.movie_view, name="movie_view"),
    path('liveconcerts/<int:id>', views.liveconcerts_view, name="liveconcerts_view"),
    path('comedy/<int:id>', views.comedyshows_view, name="comedyshows_view"),
    path('events/<int:id>', views.event_view, name="event_view"),
    path('amusement/<int:id>/', views.amusements_view, name="amusements_view"),
    
    # Public URLs
    path('contactus/', views.contactus, name="contactus"),
    path('aboutus/', views.aboutus, name="aboutus"),
    path('help center/', views.helpcenter, name="helpcenter"),
    path('terms & conditions/', views.termsandconditions, name="terms & conditions"),
    path('privacy & policy/', views.privacy_policy, name="privacy & policy"),
    path('refund & policy/', views.refundpolicy, name="refund & policy"),

    #Ticket Booking 
    path('movies/ticket_booking/<int:movie_id>',views.book_movie_tickets,name="book_movie_tickets"),
    path('movies/screens/<int:screen_id>/seats/',views.get_screen_seats,name="get_screen_seats"),
    path('liveconcerts/ticket_booking/<int:concert_id>/',views.liveconcerts_book_ticket,name="liveconcerts_book_ticket"),
    path('liveconcerts/ticket_success/<int:booking_id>/',views.ticket_success,name="ticket_success"),
    path('amusements/amusements_book_tickets/<int:park_id>/',views.amusements_book_tickets,name="amusements_book_tickets"),
    path('comedy_shows/book_comedy_tickets/<int:pk>/',views.book_comedy_tickets,name="book_comedy_tickets"),
    path('event_booking/ticket_booking/<int:business_event_id>/',views.event_book_tickets,name="event_book_tickets"),
    
    
    
    # Models Code
    path('admin/get-park-tickets/<int:park_id>/', views.get_park_tickets, name='get_park_tickets'),
    path('admin/get-ticket-details/<int:ticket_id>/', views.get_ticket_details, name='get_ticket_details'),
    path('admin/get-park-price/<int:park_id>/', views.get_park_price, name='get_park_price'),


    # Profile URl's 
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),


    # Forgot-password
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),

    path('settings/', views.settings_view, name='settings_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)