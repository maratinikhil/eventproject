from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed,post_save
from django.dispatch import receiver
import math
import uuid



class User(models.Model):
    firstname = models.CharField(max_length=50,null=True,blank=True)
    lastname = models.CharField(max_length=50,null=True,blank=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=10,unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.email
    
class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    available_seats = models.PositiveIntegerField()
    ticket_price = models.DecimalField(max_digits=8,decimal_places=2)
    image = models.ImageField(upload_to='events/',blank=True,null=True)

    def __str__(self):
        return self.name
    
class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    language = models.CharField(max_length=50, choices=[
        ("Hindi","Hindi"),
        ("English","English"),
        ("Telugu","Telugu")
    ])
    duration = models.DurationField(help_text="Duration of the movie (HH:MM:SS)")
    director = models.CharField(max_length=100, blank=True, null=True)
    cast = models.TextField(blank=True, null=True)
    genre = models.CharField(max_length=100, choices=[
        ("Action","Action"),
        ("Comedy","Comedy"),
        ("Drama","Drama"),
        ("Thriller","Thriller"),
        ("Horror","Horror"),
        ("Sci-Fi","Sci-Fi"),
        ("Romance","Romance")
    ])
    ticket_price = models.DecimalField(max_digits=8,decimal_places=2)
    available_seats = models.PositiveIntegerField()
    image = models.ImageField(upload_to='movies/',blank=True,null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.0, blank=True, null=True)
    popularity = models.CharField(max_length=20, default='Hot', choices=[
        ('Hot', 'Hot'),
        ('Trending', 'Trending'),
        ('New Release', 'New Release'),
        ('Blockbuster', 'Blockbuster'),
    ])

    def __str__(self):
        return f"{self.title} ({self.language})"
    

def get_row_letter(n):
    return chr(65+n)


class MovieScreen(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="screens")
    screen_name = models.CharField(max_length=100, default="Screen 1")
    total_rows = models.PositiveIntegerField(default=10)
    seats_per_row = models.PositiveIntegerField(default=12)

    premium_price_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('750.00'))
    executive_price_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('500.00'))
    normal_price_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('350.00'))

    premium_rows_end = models.PositiveIntegerField(default=3, help_text="Rows 1 to this number are premium")
    executive_rows_end = models.PositiveIntegerField(default=6, help_text="Rows after premium to this number are executive")


    def __str__(self):
        return f"{self.screen_name} - {self.movie.title}"

    def get_seat_type_for_row(self, row_number):
    # This method might need adjustment based on your new seating logic
    # You may want to calculate based on actual seat position rather than row
        total_seats = self.movie.available_seats
        seats_per_row = self.seats_per_row
        
        # Calculate which seats are in this row
        row_start_seat = (row_number - 1) * seats_per_row + 1
        row_end_seat = min(row_number * seats_per_row, total_seats)
        
        # For simplicity, you might want to determine the predominant seat type in this row
        # Or you can remove this method if you're handling seat types differently in the UI
        return 'normal'  # Default, adjust as needed
        

    def get_price_for_seat_type(self,seat_type):
        if seat_type == 'premium':
            return self.premium_price_multiplier
        elif seat_type == 'executive':
            return self.executive_price_multiplier
        else:
            return  self.normal_price_multiplier

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        total_seats = self.movie.available_seats
        seats_per_row = self.seats_per_row
        
        # Calculate number of rows required
        required_rows = math.ceil(total_seats / seats_per_row)
        
        # Delete existing seats for this screen
        TheaterSeat.objects.filter(screen=self).delete()
        
        seat_counter = 0
        premium_seats_count = 12
        executive_seats_count = 12
        
        # Calculate starting positions for premium and executive seats
        premium_start = total_seats - premium_seats_count + 1
        executive_start = total_seats - premium_seats_count - executive_seats_count + 1
        
        for row_num in range(required_rows):
            row_letter = get_row_letter(row_num)
            
            for seat_num in range(1, seats_per_row + 1):
                # Stop generating if we reach the total seat count
                if seat_counter >= total_seats:
                    break
                
                seat_counter += 1
                
                # Determine seat type based on position (last seats are premium, then executive)
                if seat_counter >= premium_start:
                    seat_type = "premium"
                elif seat_counter >= executive_start:
                    seat_type = "executive"
                else:
                    seat_type = "normal"
                
                seat_price = self.get_price_for_seat_type(seat_type)
                
                TheaterSeat.objects.create(
                    screen=self,
                    row=row_letter,
                    number=seat_num,
                    seat_type=seat_type,
                    price=seat_price
                )


class TheaterSeat(models.Model):
    SEAT_TYPES = [
        ('premium','premium'),
        ('executive','executive'),
        ('normal','normal')
    ]

    STATUS = [
        ('Available','Available'),
        ('Booked','Booked'),
        ('Blocked','Blocked')
    ]

    screen = models.ForeignKey(MovieScreen, on_delete=models.CASCADE, related_name="seats")
    row = models.CharField(max_length=2)
    number = models.PositiveBigIntegerField()
    seat_type = models.CharField(max_length=20, choices=SEAT_TYPES, default='normal')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS, default="Available")

    class Meta:
        unique_together = ['screen', 'row', 'number']
    
    def __str__(self):
        return f"{self.row}{self.number} - {self.get_seat_type_display()} - {self.price}"
    
    def save(self, *args, **kwargs):
        if not self.price or self.price == 0.00:
            self.price = self.screen.get_price_for_seat_type(self.seat_type)
        super().save(*args, **kwargs)
    

class TicketBooking(models.Model):
    user = models.ForeignKey(User ,on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    screen = models.ForeignKey(MovieScreen, on_delete=models.CASCADE)
    seats = models.ManyToManyField(TheaterSeat)

    total_price = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("2.00"))
    gst_rate = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("18.00"))
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))    
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    booked_at = models.DateTimeField(auto_now_add=True)

    def calculate_totals(self):
        total = Decimal("0.00")
        for seat in self.seats.all():
            total += seat.price
        return total.quantize(Decimal("0.01"))
    

    def save(self, *args, **kwargs):
        # First, save the object to get a primary key (needed for ManyToMany)
        self.gst_amount = (self.total_price * self.gst_rate / Decimal('100.00')).quantize(Decimal('0.01'))
        self.grand_total = (self.total_price + self.platform_fee + self.gst_amount.quantize(Decimal('0.01')))        
        super().save(*args, **kwargs)


    def __str__(self):
        seat_count = self.seats.count()
        user_identifier = self.user.username if hasattr (self.user,'username') else f'User {self.user.id}'
        return f"{user_identifier} - {self.movie.title} - {seat_count} seat(s) - ₹{self.grand_total}"


@receiver(m2m_changed, sender=TicketBooking.seats.through)
def update_seat_status(sender, instance, action, pk_set, **kwargs): 
    if action == "post_add":
        TheaterSeat.objects.filter(pk__in=pk_set).update(status="Booked")

    if action == "post_remove":
        TheaterSeat.objects.filter(pk__in=pk_set).update(status="Available")


def index_to_row_label(index: int) -> str:
    # index: 0 -> 'A', 25 -> 'Z', 26 -> 'AA', ...
    label = ""
    while True:
        index, rem = divmod(index, 26)
        label = chr(65 + rem) + label
        if index == 0:
            break
        index -= 1
    return label


class ComedyShow(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    comedian_name = models.CharField(max_length=100)
    age_limit = models.PositiveIntegerField(default=18)
    ticket_price = models.DecimalField(max_digits=8,decimal_places=2)
    available_seats = models.PositiveIntegerField()
    image = models.ImageField(upload_to='comedy/',blank=True,null=True)
    comedy_type = models.CharField(max_length=50, default='Stand-up', choices=[
        ('Stand-up', 'Stand-up'),
        ('Improv', 'Improv'),
        ('Sketch', 'Sketch'),
        ('Roast', 'Roast'),
    ])
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    duration = models.PositiveIntegerField(default=90, help_text="Duration in minutes")
    popularity = models.CharField(max_length=20, default='Popular', choices=[
        ('Popular', 'Popular'),
        ('Trending', 'Trending'),
        ('New', 'New'),
        ('Sold Out', 'Sold Out'),
    ])
    experience = models.CharField(max_length=100, default='Professional Comedian')


    def __str__(self):
        return self.title
    

class ComedyShowSeat(models.Model):
    SEAT_TYPES = [
        ("VIP_EARLY_A_E","VIP Early bird (A-E)"),
        ("VIP_EARLY_F_M","VIP Early bird (F-M)"),
        ("PREMIUM","Premium"),
        ("BALCONY","Balcony"),
    ]

    comedy_show = models.ForeignKey(ComedyShow,on_delete=models.CASCADE,related_name='seats')
    row = models.CharField(max_length=2)
    number = models.PositiveIntegerField()
    seat_type = models.CharField(max_length=50,choices=SEAT_TYPES)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('comedy_show', 'row', 'number')

    def __str(self):
        return f"{self.row}{self.number} - {self.get_seat_type_display()} - {self.price}"


class BookingComedyShow(models.Model):
    booking_id = models.CharField(max_length=20,unique=True,editable=False)
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    comedy_show = models.ForeignKey(ComedyShow,on_delete=models.CASCADE)
    seats = models.ManyToManyField(ComedyShowSeat)
    booking_date = models.DateTimeField()
    ticket_price_total = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    gst_percentage = models.DecimalField(max_digits=5,decimal_places=2,default=0)
    gst_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    grand_total = models.DecimalField(max_digits=10,decimal_places=2,default=0)

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = f"BK-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)
        seats_qs = self.seats.all()
        if seats_qs.exists():
            total_price = sum([seat.price for seat in seats_qs])
            total_price = Decimal(total_price).quantize(Decimal('0.01'))
            self.ticket_price_total = total_price
            self.gst_amount = (self.ticket_price_total * self.gst_percentage / Decimal('100.00')).quantize(Decimal('0.01'))
            self.grand_total = (self.ticket_price_total + self.gst_amount).quantize(Decimal('0.01'))
            super().save(update_fields=['ticket_price_total', 'gst_amount', 'grand_total'])

    def __str__(self):
        return f"{self.booking_id} - {self.user.username}"
    
@receiver(post_save, sender=ComedyShow)
def generate_comedy_show_seats(sender, instance, created, **kwargs):
    """
    Generate seats only when a ComedyShow is first created.
    Section row allocation (non-overlapping):
      - VIP_EARLY_A_E : rows A-E (5 rows)      : 6 seats per row
      - VIP_EARLY_F_M : rows F-M (8 rows)      : 6 seats per row
      - PREMIUM       : rows N-S (6 rows)      : 8 seats per row
      - BALCONY       : rows T-AE (12 rows)    : 12 seats per row
    (Rows are contiguous and unique across sections.)
    """
    if not created:
        return

    # seat_plan entry: (row_start_index, number_of_rows, seats_per_row)
    seat_plan = {
        'VIP_EARLY_A_E': (0, 5, 6),   # A..E
        'VIP_EARLY_F_M': (5, 8, 6),   # F..M
        'PREMIUM':       (13, 6, 8),  # N..S (N index=13)
        'BALCONY':       (19, 12, 12) # T.. (12 rows)
    }

    # create seats
    for seat_type, (start_index, rows_count, seats_per_row) in seat_plan.items():
        for i in range(rows_count):
            row_label = index_to_row_label(start_index + i)
            for number in range(1, seats_per_row + 1):
                # create seat
                ComedyShowSeat.objects.create(
                    comedy_show=instance,
                    row=row_label,
                    number=number,
                    seat_type=seat_type,
                    price=instance.ticket_price,
                    is_booked=False
                )

    total_seats = ComedyShowSeat.objects.filter(comedy_show=instance).count()
    instance.available_seats = total_seats
    ComedyShow.objects.filter(pk=instance.pk).update(available_seats=total_seats)     


class LiveConcert(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    artist_name = models.CharField(max_length=100)
    music_genre = models.CharField(max_length=100)

    # Ticket Pricing
    vvip_ticket_price = models.DecimalField(max_digits=8, decimal_places=2, default=2500)
    vip_ticket_price = models.DecimalField(max_digits=8, decimal_places=2, default=2000)
    couples_ticket_price = models.DecimalField(max_digits=8, decimal_places=2, default=1800)
    normal_ticket_price = models.DecimalField(max_digits=8, decimal_places=2, default=1500)

    # Taxes & Fees
    gst_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=18)  # 18%
    gst_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    province_fee = models.DecimalField(max_digits=8, decimal_places=2, default=2)
    convenience_fee = models.DecimalField(max_digits=8, decimal_places=2, default=5)
    charity_fee = models.DecimalField(max_digits=8, decimal_places=2, default=2)

    available_seats = models.PositiveIntegerField()
    image = models.ImageField(upload_to='concerts/', blank=True, null=True)

    def save(self, *args, **kwargs):
        # Example GST calculation using normal ticket price (adjust if needed)
        if self.normal_ticket_price and self.gst_percentage:
            self.gst_amount = (self.normal_ticket_price * self.gst_percentage) / 100

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.artist_name}"

class LiveConcertTicketBooking(models.Model):

    TICKET_TYPES = (
        ('VVIP', 'VVIP Ticket'),
        ('VIP', 'VIP Ticket'),
        ('COUPLES', 'Couples Ticket'),
        ('NORMAL', 'Normal Ticket'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    concert = models.ForeignKey(LiveConcert, on_delete=models.CASCADE, related_name="bookings")

    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPES)
    quantity = models.PositiveIntegerField(default=1)

    # Price breakdown
    base_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    booked_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=20, 
        choices=[("PENDING", "Pending"), ("PAID", "Paid"), ("FAILED", "Failed")],
        default="PENDING"
    )

    def calculate_base_price(self):
        if self.ticket_type == 'VVIP':
            return self.concert.vvip_ticket_price
        elif self.ticket_type == 'VIP':
            return self.concert.vip_ticket_price
        elif self.ticket_type == 'COUPLES':
            return self.concert.couples_ticket_price
        return self.concert.normal_ticket_price

    def save(self, *args, **kwargs):

        # 1. Base ticket price
        price_per_ticket = self.calculate_base_price()
        self.base_price = price_per_ticket * self.quantity

        # 2. GST
        self.gst_amount = (self.base_price * self.concert.gst_percentage) / Decimal(100)

        # 3. Other fees (province, convenience, charity)
        fee_total = (
            self.concert.province_fee +
            self.concert.convenience_fee +
            self.concert.charity_fee
        )

        self.total_fees = fee_total * self.quantity

        # 4. Final payable amount
        self.total_amount = self.base_price + self.gst_amount + self.total_fees

        # 5. Deduct seats from the concert (only on new booking)
        if not self.pk:  
            if self.quantity > self.concert.available_seats:
                raise ValueError("Not enough seats available!")
            self.concert.available_seats -= self.quantity
            self.concert.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email} - {self.ticket_type} ({self.quantity}) for {self.concert.title}"


class AmusementPark(models.Model):
    park_name = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    rides_available = models.IntegerField()
    family_friendly = models.BooleanField(default=True)
    ticket_price = models.DecimalField(max_digits=8,decimal_places=2)
    available_seats = models.PositiveIntegerField()
    image = models.ImageField(upload_to='perks/',blank=True,null=True)

    def __str__(self):
        return self.park_name


class AmusementTicket(models.Model):

    TICKET_CATEGORY = (
        ('regular', 'Regular'),
        ('offer', 'Offer'),
        ('fasttrack', 'Fasttrack'),
    )

    SUB_CATEGORY = (
        ('adult', 'Adult'),
        ('child', 'Child'),
        ('senior', 'Senior Citizen'),
        ('student', 'Student Offer'),
        ('defence', 'Defence Family'),
        ('fasttrack_adult_buffet', 'Fasttrack Adult + Buffet'),
        ('fasttrack_child_buffet', 'Fasttrack Child + Buffet'),
        ('fasttrack_adult', 'Fasttrack Adult'),
        ('fasttrack_child', 'Fasttrack Child'),
    )

    amusement_park = models.ForeignKey(
        AmusementPark,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    category = models.CharField(max_length=20, choices=TICKET_CATEGORY)
    sub_category = models.CharField(max_length=50, choices=SUB_CATEGORY)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    discount_percent = models.PositiveIntegerField(default=0, help_text="Discount %")
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    gst_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    age_limit = models.CharField(max_length=100, blank=True, null=True)
    height_limit = models.CharField(max_length=100, blank=True, null=True)
    id_proof_required = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        # For non-Wonderla parks, auto-fill category, sub_category and base_price
        if self.amusement_park and not self.amusement_park.park_name.lower().startswith('wonderla'):
            # Set default category and sub_category if not provided
            if not self.category:
                self.category = 'regular'
            if not self.sub_category:
                self.sub_category = 'adult'
            # Use park's ticket_price as base_price
            if not self.base_price or self.base_price == 0:
                self.base_price = self.amusement_park.ticket_price
        
        # Calculate totals
        if self.base_price:
            discounted_price = self.base_price - (self.base_price * self.discount_percent / 100)
            self.gst_amount = discounted_price * (self.gst_percent / 100)
            self.grand_total = discounted_price + self.gst_amount
        else:
            self.gst_amount = 0
            self.grand_total = 0
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.amusement_park.park_name} – {self.get_category_display()} – {self.get_sub_category_display()}"
    


class AmusementBooking(models.Model):
    booking_id = models.CharField(max_length=12,unique=True,editable=False)
    amusement_park = models.ForeignKey(AmusementPark,on_delete=models.CASCADE,related_name='bookings')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    total_amount = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    total_gst = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    grand_total = models.DecimalField(max_digits=10,decimal_places=2,default=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self,*args,**kwargs):
        if not self.booking_id:
            self.booking_id = str(uuid.uuid4()).split('-')[0].upper()
        super().save(*args,**kwargs)

    def get_available_ticket_types(self):
        return self.amusement_park.tickets.all()
    
    def calculate_total(self):
        items = self.items.all()
        self.total_amount = sum([item.subtotal for item in items]) or 0
        self.total_gst = sum([item.gst_amount for item in items]) or 0
        self.grand_total = sum([item.total_with_gst for item in items]) or 0
        self.save()

    def __str__(self):
        return f"Booking {self.booking_id} - {self.customer_name}"

class AmusementBookingItem(models.Model):
    booking = models.ForeignKey(AmusementBooking, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    other_booking = models.ForeignKey('OtherAmusementBooking', on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    ticket_type = models.ForeignKey(AmusementTicket, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18.00, editable=False)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    total_with_gst = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)

    def save(self, *args, **kwargs):
        # Handle OtherAmusementBooking (non-Wonderla simple bookings)
        if self.other_booking and not self.ticket_type:
            park = self.other_booking.amusement_park
            # Get or create a generic ticket for this park
            generic_ticket, created = AmusementTicket.objects.get_or_create(
                amusement_park=park,
                category='regular',
                sub_category='adult',
                defaults={
                    'base_price': self.other_booking.base_price,
                    'discount_percent': 0,
                    'gst_percent': self.other_booking.gst_percent,
                    'age_limit': 'General Admission',
                    'height_limit': 'No restrictions',
                    'id_proof_required': False,
                }
            )
            self.ticket_type = generic_ticket
            # Copy values from other_booking
            self.quantity = self.other_booking.quantity
            self.base_price = self.other_booking.base_price
            self.gst_percent = self.other_booking.gst_percent

        # Handle regular AmusementBooking (existing Wonderla logic)
        elif not self.ticket_type and self.booking and self.booking.amusement_park:
            park = self.booking.amusement_park
            if not park.park_name.lower().startswith('wonderla'):
                # Get or create a generic ticket for this park
                generic_ticket, created = AmusementTicket.objects.get_or_create(
                    amusement_park=park,
                    category='regular',
                    sub_category='adult',
                    defaults={
                        'base_price': park.ticket_price,
                        'discount_percent': 0,
                        'gst_percent': 18.00,
                        'age_limit': 'General Admission',
                        'height_limit': 'No restrictions',
                        'id_proof_required': False,
                    }
                )
                self.ticket_type = generic_ticket
        
        # For Wonderla - use ticket_type prices (existing Wonderla logic)
        if self.ticket_type:
            # Check if it's a Wonderla ticket by checking the park name
            try:
                if self.ticket_type.amusement_park.park_name.lower().startswith('wonderla'):
                    self.base_price = self.ticket_type.base_price
                    self.discount_percent = self.ticket_type.discount_percent
                    self.gst_percent = self.ticket_type.gst_percent
            except:
                pass
        
        # For other parks in regular bookings - use amusement_park ticket_price
        elif self.booking and self.booking.amusement_park:
            try:
                if not self.booking.amusement_park.park_name.lower().startswith('wonderla'):
                    self.base_price = self.booking.amusement_park.ticket_price
                    self.discount_percent = 0  # No discount for other parks
                    self.gst_percent = 18.00   # Default GST
            except:
                pass
        
        # Calculate totals
        base_price = self.base_price or 0
        discount_percent = self.discount_percent or 0
        gst_percent = self.gst_percent or 0
        quantity = self.quantity or 1
        
        discounted_price = base_price - (base_price * discount_percent / 100)
        self.subtotal = discounted_price * quantity
        self.gst_amount = (discounted_price * (gst_percent / 100)) * quantity
        self.total_with_gst = self.subtotal + self.gst_amount
        
        super().save(*args, **kwargs)

    def __str__(self):
        if self.other_booking:
            return f"{self.other_booking.amusement_park.park_name} - Simple Booking * {self.quantity}"
        elif self.ticket_type:
            return f"{self.ticket_type.amusement_park.park_name} - {self.ticket_type.get_sub_category_display()} * {self.quantity}"
        elif self.booking and self.booking.amusement_park:
            return f"{self.booking.amusement_park.park_name} - General Ticket * {self.quantity}"
        else:
            return f"General Ticket * {self.quantity}"

class OtherAmusementBooking(models.Model):
    booking_id = models.CharField(max_length=12, unique=True, editable=False)
    amusement_park = models.ForeignKey('AmusementPark', on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    quantity = models.PositiveIntegerField(default=1)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=18.00)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.booking_id:
            self.booking_id = str(uuid.uuid4()).split('-')[0].upper()
        
        # Auto-set base_price from park if not set
        if not self.base_price and self.amusement_park:
            self.base_price = self.amusement_park.ticket_price
        
        # Calculate totals
        if self.base_price and self.quantity:
            self.subtotal = self.base_price * self.quantity
            self.gst_amount = (self.base_price * (self.gst_percent / 100)) * self.quantity
            self.grand_total = self.subtotal + self.gst_amount
        
        super().save(*args, **kwargs)
        
        # Create corresponding AmusementBookingItem
        self.create_booking_item()

    def create_booking_item(self):        
        AmusementBookingItem.objects.get_or_create(
            other_booking=self,
            defaults={
                'quantity': self.quantity,
                'base_price': self.base_price,
                'gst_percent': self.gst_percent,
                'subtotal': self.subtotal,
                'gst_amount': self.gst_amount,
                'total_with_gst': self.grand_total,
            }
        )

    def __str__(self):
        return f"OtherBooking {self.booking_id} - {self.customer_name}"

    def get_park_name(self):
        return self.amusement_park.park_name if self.amusement_park else "No Park"