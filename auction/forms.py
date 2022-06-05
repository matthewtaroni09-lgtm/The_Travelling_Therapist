from django import forms
from .models import PROVINCES, Auction, Bid, Account, User, UserType
from django.contrib.auth.forms import UserCreationForm
import random

class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ( 
            'placementStart', 
            'placementEnd', 
            'reservePrice',
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
    x = list(range(1,101))
    first_name = forms.CharField(initial='John')
    last_name = forms.CharField(initial='Doe')
    clinicName = forms.CharField()
    city = forms.CharField(initial='Burlington')
    province = forms.ChoiceField(choices=PROVINCES)
    username = forms.CharField(initial='loribine' + str(random.choice(x)) + '@gmail.com')
    user_type = forms.ModelChoiceField(queryset=UserType.objects.all())
    imageOne = forms.ImageField()

    class Meta:
        model = User
        fields = ('user_type', 'clinicName', 'first_name', 'last_name', 'username', 'city', 'province', 'password1' ,'password2', 'imageOne' )
        # labels = {'username': 'Email'}
        widgets = {
            'imageOne': forms.ImageField()
        }

class CreateUserForm(UserCreationForm):
    # first_name = forms.CharField(initial='John')
    # last_name = forms.CharField(initial='Doe')
    # clinicName = forms.CharField(initial='Doe')
    # userType = forms.ModelChoiceField(queryset=UserType.objects.all())
    # # province = forms.ModelChoiceField(queryset=PROVINCES.)
    # city = forms.CharField()
    # about = forms.CharField()
    # imageOne = forms.ImageField()
    class Meta:
        model = User
        # fields = ['username', 'first_name', 'last_name', 'userType', 'clinicName', 'city', 'about']#,'province', 'imageOne', 'imageTwo', 'imageThree', 'imageFour', 'practiceArea']
        fields = ['username', 'first_name', 'last_name', 'password1' ,'password2']

class UserForm(forms.ModelForm):
    email = forms.EmailField()  # This For Additional Field

    class Meta:
        model = User
        fields = ['email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['clinicName', 'city', 'province', 'about', 'imageOne', 'imageTwo', 'imageThree', 'imageFour', 'practiceArea']