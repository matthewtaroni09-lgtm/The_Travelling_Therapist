from cgitb import lookup
from pyexpat import model

from django import forms
import django_filters
from .models import Auction

class AuctionFilter(django_filters.FilterSet):
    print("in fi;ter")
    auctions_list = Auction.objects.filter(active=True)
    # auctions_list = Auction.objects.all()
    location_list = ()
    location_check_list = []

    status_list = ()
    status_check_list = []

    # Save for future update
    #therapist_list = ()
    #therapist_check_list = []
    
    therapist_list = []
    for auction in auctions_list:
        print(auction.clinic.city)
        if auction.clinic.city not in location_check_list:
            locations = ()
            locations = (auction.clinic.city, auction.clinic.city)
            location_list = (*location_list, locations)
            location_check_list.append(auction.clinic.city)

        # print(auction.active)
        # if auction.active not in status_check_list:
        #     statuses = ()
        #     statuses = (auction.active, auction.active)
        #     status_list = (*status_list, statuses)
        #     status_check_list.append('Open')

        # if auction.clinic.userType not in therapist_check_list:
        #     therapist = ()
        #     therapist = (auction.clinic.userType, auction.clinic.userType)
        #     therapist_list = (*therapist_list, therapist)
        #     therapist_check_list.append(auction.clinic.userType)

    city = django_filters.ChoiceFilter(field_name='clinic__city', choices=location_list)
    # status = django_filters.ChoiceFilter(field_name='auction__active', choices=status_list)
    # online = django_filters.filters.BooleanFilter(field_name='auction__active', widget=forms.CheckboxInput)
    # userType = django_filters.ChoiceFilter(field_name='clinic__userType__name', choices=therapist_list)
    class Meta:
        model = Auction
        fields = ()