from django import forms
from .models import Auction, Bid, Account, User, UserType
from django.contrib.auth.forms import UserCreationForm

class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = (
            'auctionStart', 
            'auctionEnd',
            'reservePrice', 
            'placementStart', 
            'placementEnd', 
            'payFrequency', 
            'mondayStart', 
            'mondayEnd',
            'tuesdayStart',
            'tuesdayEnd',
            'wednesdayStart',
            'wednesdayEnd',
            'thursdayStart',
            'thursdayEnd',
            'fridayStart',
            'fridayEnd',
            'saturdayStart',
            'saturdayEnd',
            'sundayStart',
            'sundayEnd',
            'comments',
            'MSK',
            'neuro',
            'cardioResp',
            'underEightteen',
            'eightteenToSixtyFive',
            'overSixtyFive'
        )
        # labels = {}
        widgets = {
            'auctionStart': forms.DateTimeInput(format=('%Y-%m-%d'), attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}),
            'auctionEnd': forms.DateTimeInput(format=('%Y-%m-%d %H:%M'), attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}),
            'placementStart': forms.DateInput(format=('%Y-%m-%d'), attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}),
            'placementEnd': forms.DateInput(format=('%Y-%m-%d'), attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}),
            'mondayStart': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'mondayEnd': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'tuesdayStart': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'tuesdayEnd': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'wednesdayStart': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'wednesdayEnd': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'thursdayStart': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'thursdayEnd': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'fridayStart': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'fridayEnd': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'saturdayStart': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'saturdayEnd': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'sundayStart': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'sundayEnd': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'time'}),
            'comments': forms.Textarea(attrs={'placeholder': 'Tell us about your clinic...', 'rows': '4'})
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
    city = forms.CharField()
    # user_type = forms.ModelChoiceField(queryset=UserType.objects.filter())
    user_type = forms.ModelChoiceField(queryset=UserType.objects.exclude(name__endswith='Clinic'))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'license_number', 'username', 'city', 'user_type', 'password1' ,'password2' )
        labels = {'username': 'Email'}

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1' ,'password2')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('licenseNumber', 'city')