from cgitb import lookup
from pyexpat import model
import django_filters
from .models import Auction

class AuctionFilter(django_filters.FilterSet):
    auctions_list = Auction.objects.filter(active=True)
    location_list = ()
    therapist_list = ()
    location_check_list = []
    therapist_check_list = []
    
    therapist_list = []
    for auction in auctions_list:
        if auction.clinic.city not in location_check_list:
            locations = ()
            locations = (auction.clinic.city, auction.clinic.city)
            location_list = (*location_list, locations)
            location_check_list.append(auction.clinic.city)

        if auction.clinic.userType not in therapist_check_list:
            therapist = ()
            therapist = (auction.clinic.userType, auction.clinic.userType)
            therapist_list = (*therapist_list, therapist)
            therapist_check_list.append(auction.clinic.userType)

    city = django_filters.ChoiceFilter(field_name='clinic__city', choices=location_list)
    userType = django_filters.ChoiceFilter(field_name='clinic__userType__name', choices=therapist_list)
    class Meta:
        model = Auction
        fields = ()