from cgitb import lookup
from pyexpat import model

from django import forms
from auction.scheduled_tasks import auction_closed
import django_filters
from .models import Auction
from django.db.models import Q

class AuctionFilter(django_filters.FilterSet):
    auctions_list = Auction.objects.filter((Q(active=True) | Q(closed=True)) & Q(deleted=False))
    location_list = ()
    location_check_list = []
    AUCTION_STATUSES = (
        (True, 'Active'),
        (False, 'Closed'),
    )

    for auction in auctions_list:
        if auction.clinic.city not in location_check_list:
            locations = ()
            locations = (auction.clinic.city, auction.clinic.city)
            location_list = (*location_list, locations)
            location_check_list.append(auction.clinic.city)

    city = django_filters.ChoiceFilter(label='City', field_name='clinic__city', choices=location_list)
    active = django_filters.ChoiceFilter(label='Auction Status', field_name='active', choices=AUCTION_STATUSES)
    clinic = django_filters.CharFilter(label='Clinic', field_name='clinic__clinicName', lookup_expr='icontains', widget=forms.TextInput(attrs={
            'placeholder': 'Search auctions'}))
   
    class Meta:
        model = Auction
        fields = ['city', 'active', 'clinic']