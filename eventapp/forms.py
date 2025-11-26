from django import forms
from .models import Event, ComedyShow, Movie, LiveConcert, AmusementPark,AmusementTicket,BookingComedyShow

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"


class ComedyShowForm(forms.ModelForm):
    class Meta:
        model = ComedyShow
        fields = "__all__"

class BookingComedyShowForm(forms.ModelForm):
    class Meta:
        model = BookingComedyShow
        fields = ['number_of_tickets']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Show available seats info for existing bookings
            available = self.instance.comedy_show.available_seats
            self.fields['number_of_tickets'].help_text = f"Available seats: {available}"
        elif self.initial.get('comedy_show'):
            # For new bookings with pre-selected comedy show
            comedy_show = ComedyShow.objects.get(pk=self.initial['comedy_show'])
            available = comedy_show.available_seats
            self.fields['number_of_tickets'].help_text = f"Available seats: {available}"
        else:
            # For new booking without comedy show selected
            self.fields['number_of_tickets'].help_text = "Select a comedy show to see available seats"    
    
    def clean(self):
        cleaned_data = super().clean()
        comedy_show = cleaned_data.get('comedy_show')
        number_of_tickets = cleaned_data.get('number_of_tickets')
        
        if comedy_show and number_of_tickets:
            current_available = comedy_show.available_seats
            if number_of_tickets > current_available:
                raise forms.ValidationError(
                    f"Only {current_available} seats available. You requested {number_of_tickets}."
                )
            if number_of_tickets <= 0:
                raise forms.ValidationError("Number of tickets must be at least 1.")
        
        return cleaned_data

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = "__all__"


class LiveConcertForm(forms.ModelForm):
    class Meta:
        model = LiveConcert
        fields = "__all__"

class AmusementTicketForm(forms.ModelForm):
    class Meta:
        model = AmusementTicket
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        amusement_park = cleaned_data.get('amusement_park')
        base_price = cleaned_data.get('base_price')
        
        # Only validate if amusement_park is selected and it's not Wonderla
        if amusement_park and not amusement_park.park_name.lower().startswith('wonderla'):
            # For non-Wonderla parks, base_price must match park's ticket_price
            if base_price != amusement_park.ticket_price:
                raise forms.ValidationError(
                    f"For {amusement_park.park_name}, base price must be {amusement_park.ticket_price}"
                )
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get amusement_park from instance or initial data
        amusement_park = None
        
        # For existing instances
        if self.instance and self.instance.pk:
            try:
                amusement_park = self.instance.amusement_park
            except AmusementPark.DoesNotExist:
                amusement_park = None
        # For new instances, check initial data
        elif 'initial' in kwargs and 'amusement_park' in kwargs['initial']:
            amusement_park = kwargs['initial']['amusement_park']
        # For form submissions, we'll handle in clean method
        
        # If we have a non-Wonderla park, adjust the form
        if amusement_park and not amusement_park.park_name.lower().startswith('wonderla'):
            # Set initial value for base_price
            self.fields['base_price'].initial = amusement_park.ticket_price
            
            # Make base_price read-only
            self.fields['base_price'].widget.attrs['readonly'] = True
            self.fields['base_price'].widget.attrs['style'] = 'background-color: #f8f9fa;'
            
            # Make category and sub_category optional and set defaults
            self.fields['category'].required = False
            self.fields['sub_category'].required = False
            
            # Set default values if not already set
            if not self.instance.pk:  # Only for new instances
                self.fields['category'].initial = 'regular'
                self.fields['sub_category'].initial = 'adult'