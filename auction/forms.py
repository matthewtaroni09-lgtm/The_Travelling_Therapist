from django import forms
from .models import Auction, Bid, Account, User
from django.contrib.auth.forms import UserCreationForm

class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ('auctionStart', 'auctionEnd', 'reservePrice', 'placementStart', 'placementEnd', 'payFrequency', 'mondayStart', 'mondayEnd')
        labels = {}
        widgets = {
            'auctionStart': forms.DateTimeInput(format=('%Y-%m-%d'), attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}),
            'auctionEnd': forms.DateTimeInput(format=('%Y-%m-%d %H:%M'), attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'datetime'}),
            'reservePrice': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Reserve Price'}),
            'placementStart': forms.DateInput(format=('%Y-%m-%d'), attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}),
            'placementEnd': forms.DateInput(format=('%Y-%m-%d'), attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}),
            'mondayStart': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'mondayEnd': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
        }

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ('amount', )
        labels = {}
        widgets = {
            'amount': forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Bid Amount'})
            }

class RegisterTherapist(UserCreationForm):
    first_name = forms.CharField()
    last_name = forms.CharField()
    license_number = forms.CharField()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'license_number', 'username', 'password1' ,'password2' )
        labels = {'username': 'Email'}

