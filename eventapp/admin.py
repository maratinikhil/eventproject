from django.contrib import admin
from django.utils.safestring import mark_safe
from django import forms
from django.utils.html import format_html
from .models import Event,ComedyShow,Movie,LiveConcert,AmusementPark,TicketBooking,MovieScreen,TheaterSeat,LiveConcertTicketBooking,AmusementTicket,AmusementBooking,AmusementBookingItem,OtherAmusementBooking,BookingComedyShow,BookingsEvent
from .forms import AmusementTicketForm,BookingComedyShowForm

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'location', 
        'date', 
        'time', 
        'ticket_price', 
        'total_seats',
        'available_seats_display',
        'booked_seats_display',
        'booking_percentage_display',
        'is_sold_out_display'
    ]

    search_fields = ['name', 'location']
    list_filter = ['date', 'location']

    readonly_fields = [
        'available_seats',
        'booked_seats',
        'booking_percentage'
    ]

    # DISPLAY SAFE FIELDS


    def available_seats_display(self, obj):
        if obj.available_seats is None:
            return "-"
        
        seats = obj.available_seats

        if seats == 0:
            return format_html('<span style="color: red; font-weight: bold;">SOLD OUT (0)</span>')
        elif seats <= 10:
            return format_html('<span style="color: orange; font-weight: bold;">{} (Low)</span>', seats)
        else:
            return format_html('<span style="color: green; font-weight: bold;">{}</span>', seats)

    available_seats_display.short_description = 'Available Seats'

    def booked_seats_display(self, obj):
        if obj.booked_seats is None:
            return "0"
        return obj.booked_seats

    booked_seats_display.short_description = 'Booked'

    def booking_percentage_display(self, obj):
        percentage = obj.booking_percentage or 0

        if percentage >= 90:
            color = 'red'
            status = 'Almost Full'
        elif percentage >= 70:
            color = 'orange'
            status = 'Filling Up'
        else:
            color = 'green'
            status = 'Available'

        return format_html(
            '<span style="color: {}; font-weight: bold;">{}% ({})</span>',
            color, int(percentage), status
        )

    booking_percentage_display.short_description = 'Booking Status'

    def is_sold_out_display(self, obj):
        if obj.is_sold_out:
            return format_html('<span style="color: red; font-weight: bold;">SOLD OUT</span>')
        return format_html('<span style="color: green;">✓ Available</span>')

    is_sold_out_display.short_description = 'Status'
@admin.register(BookingsEvent)
class BookingsAdmin(admin.ModelAdmin):
    list_display = [
        'get_booking_id', 
        'get_customer_name', 
        'get_event_name', 
        'get_event_date',
        'number_of_tickets', 
        'total_amount', 
        'status', 
        'payment_status',
        'booking_date',
        'user'
    ]

    list_filter = [
        'status', 
        'payment_status', 
        'booking_date', 
        'event__date',
        'event__location',
        'user'
    ]

    search_fields = [
        'booking_id', 
        'customer_name', 
        'customer_email',
        'event__name',
        'user__username' 
    ]

    readonly_fields = [
        'get_booking_id_readonly', 
        'booking_date', 
        'total_amount',
        'get_user_display'
    ]

    exclude = ['user']

    fieldsets = (
        ('Booking Information', {
            'fields': (
                'get_booking_id_readonly', 
                'booking_date', 
                'status',
                'payment_status',
                'get_user_display'
            )
        }),
        ('Event Details', {
            'fields': (
                'event', 
                'number_of_tickets', 
                'total_amount'
            )
        }),
        ('Customer Information', {
            'fields': (
                'customer_name', 
                'customer_email', 
                'customer_phone',
                'special_request'
            )
        }),
    )
    
    def get_booking_id(self, obj):
        return obj.booking_id
    get_booking_id.short_description = "Booking ID"

    def get_customer_name(self, obj):
        return obj.customer_name
    get_customer_name.short_description = "Customer Name"

    def get_user_display(self, obj):
        if obj.user:
            return f"{obj.user.username} ({obj.user.email})"
        return "No user assigned"
    get_user_display.short_description = "User"

    def get_event_name(self, obj):
        return obj.event.name
    get_event_name.short_description = "Event Name"

    def get_event_date(self, obj):
        return obj.event.date
    get_event_date.short_description = "Event Date"

    def get_booking_id_readonly(self, obj):
        return obj.booking_id
    get_booking_id_readonly.short_description = "Booking ID"

    def available_seats_info(self, obj):
        if obj.pk:  # For existing bookings
            event = obj.event
            return f"Total: {event.total_seats}, Available: {event.available_seats}, Booked: {event.booked_seats}"
        else:  # For new bookings
            return "Select an event to see available seats"
    available_seats_info.short_description = "Event Seats Info"

    # Auto-set the current user when creating a booking
    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Only for new objects
            obj.user = request.user
            
            # Validate available seats for new confirmed bookings
            if obj.status == 'confirmed' and obj.event:
                if obj.number_of_tickets > obj.event.available_seats:
                    from django.contrib import messages
                    messages.error(request, f"Only {obj.event.available_seats} seats available!")
                    return
        
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "event":
            # Only show events that have available seats
            kwargs["queryset"] = Event.objects.filter(available_seats__gt=0)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    actions = ['mark_as_confirmed', 'mark_as_cancelled', 'mark_payment_received']

    def mark_as_confirmed(self, request, queryset):
        for booking in queryset:
            if booking.number_of_tickets <= booking.event.available_seats:
                booking.status = 'confirmed'
                booking.save()
            else:
                from django.contrib import messages
                messages.error(request, f"Not enough seats for booking {booking.booking_id}")
    mark_as_confirmed.short_description = "Mark selected bookings as confirmed"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        events_to_update = set(booking.event for booking in queryset if booking.status == 'confirmed')
        for event in events_to_update:
            event.update_available_seats()
    mark_as_cancelled.short_description = "Mark selected bookings as cancelled"
    
    def mark_payment_received(self, request, queryset):  
        queryset.update(payment_status=True)
    mark_payment_received.short_description = "Mark payment as received for selected bookings"

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'language', 'genre', 'location', 'date', 'time', 'ticket_price', 'available_seats','cast','director','rating','popularity']
    search_fields = ['title', 'language', 'genre','director','cast']
    list_filter = ['language', 'genre','date']



@admin.register(ComedyShow)
class ComedyShowAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'date', 'time', 'comedian_name', 'total_seats', 'available_seats_display', 'ticket_price')
    search_fields = ('title', 'comedian_name', 'location')
    list_filter = ('comedy_type', 'date', 'popularity')
    readonly_fields = ('available_seats_display',)
    
    def available_seats_display(self, obj):
        """Display available seats with color coding"""
        available = obj.available_seats
        total = obj.total_seats
        
        if available == 0:
            color = 'red'
            text = 'SOLD OUT'
        elif available < total * 0.2:  # Less than 20% seats left
            color = 'red'
            text = f'{available} / {total}'
        elif available < total * 0.5:  # Less than 50% seats left
            color = 'orange'
            text = f'{available} / {total}'
        else:
            color = 'green'
            text = f'{available} / {total}'
            
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    available_seats_display.short_description = 'Available Seats'

@admin.register(BookingComedyShow)
class BookingComedyShowAdmin(admin.ModelAdmin):
    form = BookingComedyShowForm
    list_display = ('booking_id', 'user', 'comedy_show', 'number_of_tickets', 'total_price', 'booking_date')
    search_fields = ('booking_id', 'user__username', 'comedy_show__title')
    readonly_fields = ('booking_id', 'total_price', 'booking_date')
    list_filter = ('booking_date', 'comedy_show')
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Force update of available seats
        obj.comedy_show.update_available_seats()

    def delete_model(self, request, obj):
        # Update seats before deletion
        comedy_show = obj.comedy_show
        super().delete_model(request, obj)
        comedy_show.update_available_seats()

@admin.register(LiveConcert)
class LiveConcertAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'artist_name', 'music_genre', 'location', 'date', 'time',
        'vvip_ticket_price', 'vip_ticket_price', 'couples_ticket_price', 'normal_ticket_price',
        'available_seats','gst_amount'
    ]

    # Editable fields in list view
    list_editable = [
        'vvip_ticket_price',
        'vip_ticket_price',
        'couples_ticket_price',
        'normal_ticket_price',
        'available_seats'
    ]

    search_fields = ['title', 'artist_name', 'music_genre']
    list_filter = ['music_genre']

    readonly_fields = ['gst_amount', 'image_preview']

    fieldsets = (
        ("Concert Info", {
            "fields": ("title", "description", "artist_name", "music_genre")
        }),
        ("Location & Timing", {
            "fields": ("location", "date", "time")
        }),
        ("Ticket Pricing", {
            "fields": (
                "vvip_ticket_price",
                "vip_ticket_price",
                "couples_ticket_price",
                "normal_ticket_price",
            )
        }),
        ("Taxes & Fees", {
            "fields": ("gst_percentage", "gst_amount", "province_fee", "convenience_fee", "charity_fee")
        }),
        ("Seats & Image", {
            "fields": ("available_seats", "image", "image_preview")
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="120" height="120" style="border-radius:8px; object-fit:cover;" />'
        return "No image uploaded"
    image_preview.allow_tags = True
    image_preview.short_description = "Preview"

@admin.register(LiveConcertTicketBooking)
class LiveConcertticketBookingAdmin(admin.ModelAdmin):

    list_display = [
        'user', 'concert', 'ticket_type', 'quantity',
        'total_amount', 'payment_status', 'booked_at'
    ]

    list_filter = ['ticket_type', 'booked_at']
    search_fields = ['user__email', 'concert__title']

    exclude = ['payment_status']

    readonly_fields = [
        'base_price',
        'gst_amount',
        'total_fees',
        'total_amount',
        'booked_at',

        # Add these!!
        'base_price_details',
        'gst_details',
        'fees_details',
        'total_details',
    ]

    fieldsets = (
        ("Customer Details", {
            "fields": ("user",)
        }),
        ("Concert Booked", {
            "fields": ("concert",)
        }),
        ("Ticket Information", {
            "fields": ("ticket_type", "quantity")
        }),
        ("Price Breakdown", {
            "fields": (
                ("base_price", "base_price_details"),
                ("gst_amount", "gst_details"),
                ("total_fees", "fees_details"),
                ("total_amount", "total_details"),
            )
        }),
    )

    def save_model(self, request, obj, form, change):
        obj.save()
        super().save_model(request, obj, form, change)

    # ----------------------
    # DETAIL FIELDS BELOW
    # ----------------------

    def base_price_details(self, obj):
        if not obj.base_price:
            return "-"
        return f"{obj.base_price}"
    base_price_details.short_description = "Base Price (₹)"

    def gst_details(self, obj):
        if not obj.gst_amount:
            return "-"
        return f"{obj.gst_amount} ({obj.concert.gst_percentage}%)"
    gst_details.short_description = "GST"

    def fees_details(self, obj):
        if not obj.total_fees:
            return "-"
        p = obj.concert.province_fee
        c = obj.concert.convenience_fee
        h = obj.concert.charity_fee
        return (
            f"Province Fee: {p}\n"
            f"Convenience Fee: {c}\n"
            f"Charity Fee: {h}"
        )
    fees_details.short_description = "Fees"

    def total_details(self, obj):
        if not obj.total_amount:
            return "-"
        return f"{obj.total_amount}"
    total_details.short_description = "Grand Total (₹)"


class TicketInline(admin.TabularInline):
    model = AmusementTicket
    form = AmusementTicketForm
    extra = 1

    readonly_fields = (
        'gst_amount',
        'grand_total',
    )

    fields = (
        'category',
        'sub_category',
        'base_price',
        'discount_percent',
        'gst_percent',
        'gst_amount',
        'grand_total',
        'age_limit',
        'height_limit',
        'id_proof_required',
    )

    can_delete = True

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        # For non-Wonderla parks, adjust the form
        if obj and not obj.park_name.lower().startswith('wonderla'):
            formset.form.base_fields['category'].required = False
            formset.form.base_fields['sub_category'].required = False
            
        return formset


@admin.register(AmusementTicket)
class TicketAdmin(admin.ModelAdmin):
    form = AmusementTicketForm
    list_display = (
        'amusement_park',
        'category',
        'sub_category',
        'base_price',
        'discount_percent',
        'gst_percent',
        'gst_amount',
        'grand_total',
    )

    list_filter = ('category', 'sub_category', 'amusement_park')
    search_fields = ('sub_category', 'amusement_park__park_name')

    readonly_fields = ('gst_amount', 'grand_total')

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ['gst_amount', 'grand_total']
        
        # Make base_price read-only for existing non-Wonderla park tickets
        if obj and obj.pk and hasattr(obj, 'amusement_park') and obj.amusement_park:
            if not obj.amusement_park.park_name.lower().startswith('wonderla'):
                readonly_fields.append('base_price')
            
        return readonly_fields

    def save_model(self, request, obj, form, change):
        # For non-Wonderla parks, ensure category and sub_category are set
        if obj.amusement_park and not obj.amusement_park.park_name.lower().startswith('wonderla'):
            if not obj.category:
                obj.category = 'regular'
            if not obj.sub_category:
                obj.sub_category = 'adult'
                
        super().save_model(request, obj, form, change)

    class Media:
        js = ('admin/js/amusement_ticket.js',)


@admin.register(AmusementPark)
class AmusementParkAdmin(admin.ModelAdmin):
    list_display = ['park_name', 'location', 'date', 'time', 
                    'rides_available', 'family_friendly', 
                    'ticket_price', 'available_seats','ticket_count','ticket_types']
    search_fields = ['park_name', 'location']
    list_filter = ['family_friendly','date']

    inlines = [TicketInline]

    def ticket_count(self,obj):
        return obj.tickets.count()
    ticket_count.short_description = 'Total Ticket Types'

    def ticket_types(self,obj):
        tickets = obj.tickets.all()
        if not tickets:
            return "-"
        return ','.join([t.sub_category for t in tickets])
    ticket_types.short_description = "Available tickets"


class AmusementBookingItemInline(admin.TabularInline):
    model = AmusementBookingItem
    extra = 1

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "ticket_type":
            # Get park ID from various sources
            park_id = None
            
            # First try: Editing existing booking
            booking_id = request.resolver_match.kwargs.get('object_id')
            if booking_id:
                try:
                    booking = AmusementBooking.objects.get(id=booking_id)
                    park_id = booking.amusement_park_id
                except AmusementBooking.DoesNotExist:
                    pass
            
            # Second try: GET parameter (for new bookings)
            if not park_id:
                park_id = request.GET.get("amusement_park")
            
            # Third try: POST data (when form is submitted)
            if not park_id and request.method == 'POST':
                park_id = request.POST.get("amusement_park")
            
            # Filter tickets by park
            if park_id:
                kwargs["queryset"] = AmusementTicket.objects.filter(amusement_park_id=park_id)
            else:
                kwargs["queryset"] = AmusementTicket.objects.none()
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(AmusementBooking)
class AmusementBookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_id',
        'customer_name',
        'amusement_park',
        'total_amount',
        'total_gst',
        'grand_total',
        'created_at',
    )

    search_fields = (
        'booking_id',
        'customer_name',
        'customer_email',
    )

    list_filter = (
        'amusement_park',
        'created_at',
    )

    readonly_fields = (
        'booking_id',
        'total_amount',
        'total_gst',
        'grand_total',
        'created_at',
    )

    inlines = [AmusementBookingItemInline]

    fieldsets = (
        ('Booking Information', {
            'fields': (
                'booking_id',
                'amusement_park',
                'customer_name',
                'customer_email',
                'customer_phone',
            )
        }),
        ('Totals', {
            'fields': (
                'total_amount',
                'total_gst',
                'grand_total',
            )
        }),
        ('Created', {
            'fields': ('created_at',)
        }),
    )

    def get_form(self, request, obj = None, **kwargs):
        form = super().get_form(request,obj,**kwargs)

        if not obj:
            form.base_fields['amusement_park'].required = True
        return form

    def changeform_view(self, request, object_id = None, form_url = '', extra_context = None):
        if request.method == "POST" and 'amusement_park' in request.POST:
            request.session['selected_park'] = request.POST.get('amusement_park')
        elif request.method == 'GET' and 'amusement_park' in request.GET:
            request.session['selected_park'] = request.GET.get('amusement_park')

        return super().changeform_view(request, object_id, form_url, extra_context)

    # Auto-update totals when saving booking
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.calculate_total()

    # Auto-update totals when saving inline items
    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.calculate_total()

@admin.register(OtherAmusementBooking)
class OtherAmusementBookingAdmin(admin.ModelAdmin):
    list_display = [
        'booking_id',
        'customer_name',
        'get_park_name',
        'quantity',
        'base_price',
        'subtotal',
        'gst_amount',
        'grand_total',
        'created_at'
    ]

    search_fields = [
        'booking_id',
        'customer_name',
        'customer_email',
        'amusement_park__park_name'
    ]

    list_filter = ['amusement_park','created_at']

    readonly_fields = [
        'booking_id',
        'subtotal',
        'gst_amount',
        'grand_total',
        'created_at',
        'display_booking_items',
    ]

    fieldsets = (
        ('Booking Information', {
            'fields': (
                'booking_id',
                'amusement_park',
                'customer_name',
                'customer_email',
                'customer_phone',
            )
        }),
        ('Ticket Details', {
            'fields': (
                'quantity',
                'base_price',
                'gst_percent',
            )
        }),
        ('Totals', {
            'fields': (
                'subtotal',
                'gst_amount',
                'grand_total',
            )
        }),
        ('Linked Items', {
            'fields': (
                'display_booking_items',
            )
        }),
        ('Created', {
            'fields': ('created_at',)
        }),
    )

    def get_park_name(self, obj):
        return obj.amusement_park.park_name
    get_park_name.short_description = 'Amusement Park'
    get_park_name.admin_order_field = 'amusement_park__park_name'

    def display_booking_items(self, obj):
        items = obj.items.all()
        if items:
            item_list = []
            for item in items:
                item_list.append(f"{item.quantity} tickets × {item.base_price} = {item.total_with_gst}")
            return "<br>".join(item_list)
        return "No booking items created yet"
    display_booking_items.short_description = 'Linked Booking Items'
    display_booking_items.allow_tags = True

    def save_model(self, request, obj, form, change):
        # Auto-set base_price if not provided
        if not obj.base_price and obj.amusement_park:
            obj.base_price = obj.amusement_park.ticket_price
        super().save_model(request, obj, form, change)
    

@admin.register(AmusementBookingItem)
class AmusementBookingItemAdmin(admin.ModelAdmin):
    list_display = (
        'get_booking_type',
        'get_booking_id',
        'get_customer_name',
        'get_park_name',
        'get_ticket_info',
        'quantity',
        'subtotal',
        'gst_amount',
        'total_with_gst',
    )

    readonly_fields = (
        'subtotal',
        'gst_amount',
        'total_with_gst',
    )

    search_fields = (
        'booking__booking_id',
        'other_booking__booking_id',
        'booking__customer_name',
        'other_booking__customer_name',
        'ticket_type__sub_category',
    )

    list_filter = ('booking__amusement_park','other_booking__amusement_park')

    def get_booking_type(self, obj):
        if obj.other_booking:
            return "Simple Booking"
        elif obj.booking:
            return "Wonderla Booking"
        return "Unknown"
    get_booking_type.short_description = 'Booking Type'

    def get_booking_id(self, obj):
        if obj.other_booking:
            return obj.other_booking.booking_id
        elif obj.booking:
            return obj.booking.booking_id
        return "N/A"
    get_booking_id.short_description = 'Booking ID'
    get_booking_id.admin_order_field = 'booking__booking_id'

    def get_customer_name(self, obj):
        if obj.other_booking:
            return obj.other_booking.customer_name
        elif obj.booking:
            return obj.booking.customer_name
        return "N/A"
    get_customer_name.short_description = 'Customer Name'
    get_customer_name.admin_order_field = 'booking__customer_name'

    def get_park_name(self, obj):
        if obj.other_booking:
            return obj.other_booking.amusement_park.park_name
        elif obj.booking and obj.booking.amusement_park:
            return obj.booking.amusement_park.park_name
        return "N/A"
    get_park_name.short_description = 'Amusement Park'
    get_park_name.admin_order_field = 'booking__amusement_park__park_name'

    def get_ticket_info(self, obj):
        if obj.other_booking:
            return "General Admission (Simple Booking)"
        elif obj.ticket_type:
            return f"{obj.ticket_type.get_category_display()} - {obj.ticket_type.get_sub_category_display()}"
        elif obj.booking and obj.booking.amusement_park:
            return f"{obj.booking.amusement_park.park_name} - General Ticket"
        return "General Ticket"
    get_ticket_info.short_description = 'Ticket Type'



class TheaterSeatInline(admin.TabularInline):
    model = TheaterSeat
    extra = 0
    readonly_fields = ['row', 'number','seat_type','price'] 
    can_delete = False


    def has_add_permission(self, request, obj=None):
        return False
    

@admin.register(MovieScreen)
class MovieScreenAdmin(admin.ModelAdmin):
    list_display = ['screen_name','movie','total_rows','seats_per_row',
                    'premium_price_multiplier','executive_price_multiplier',
                    'normal_price_multiplier']
    inlines = [TheaterSeatInline]
    list_filter = ['movie']
    exclude = ('premium_rows_end', 'executive_rows_end')
    fieldsets = (
        ('Basic Information',{
            'fields' : ('movie','screen_name','total_rows','seats_per_row')
        }),
        ('Seat Pricing (Fixed Prices)',{
            'fields' : ('premium_price_multiplier',
                        'executive_price_multiplier',
                        'normal_price_multiplier'),
            'description': 'Set fixed prices for each seat type'
        }),
        ('Seat Type Configuration',{
            'fields' : (),
            'description': 'Premium = 6 seats, Executive = 6 seats, all within Row A'
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if change:
            for seat in obj.seats.all():
                seat.price = obj.get_price_for_seat_type(seat.seat_type)
                seat.save()


# CUSTOM ICONS
def seat_status_icon(obj):
    if obj.status == "Booked":
        return "Booked!"
    elif obj.status == "Blocked":
        return "Blocked"
    else:
        return "Available"

seat_status_icon.short_description = "Status"
seat_status_icon.allow_tags = True

@admin.register(TheaterSeat)
class TheaterSeatAdmin(admin.ModelAdmin):
    list_display = ['screen','row','number','seat_type','price',seat_status_icon]
    list_filter = ['screen','seat_type','status']
    search_fields = ['screen__screen_name','row','number','seat_type']
    readonly_fields = ['screen','row','number','seat_type','price']

    def has_add_permission(self, request):
        return False


    def is_booked(self, obj):
        return obj.status == "Booked"
    is_booked.boolean = True
    is_booked.short_description = 'Booked?'



@admin.register(TicketBooking)
class TicketBookingAdmin(admin.ModelAdmin):
    list_display = ['get_user_display','movie','screen','total_price','platform_fee','gst_rate','gst_amount','grand_total','booked_at','get_seat_count']
    list_filter = ['movie','screen','booked_at']
    readonly_fields = ['gst_amount','grand_total','booked_at']
    filter_horizontal = ['seats']

    def get_readonly_fields(self, request, obj=None):
        readonly = ['gst_amount', 'grand_total', 'booked_at']
        if obj:
            readonly += ['user', 'movie', 'screen']  
        return readonly


    def get_user_display(self, obj):
        if hasattr(obj.user, 'username'):
            return obj.user.username
        elif hasattr(obj.user, 'email'):
            return obj.user.email
        elif hasattr(obj.user, 'first_name') and obj.user.first_name:
            return f"{obj.user.first_name} {obj.user.last_name or ''}".strip()
        else:
            return f"User {obj.user.id}"
    get_user_display.short_description = 'User'
    get_user_display.admin_order_field = 'user'

    def get_seat_count(self, obj):
        return obj.seats.count()
    get_seat_count.short_description = 'Seats'


