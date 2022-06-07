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

class RegisterAcount(UserCreationForm):
    x = list(range(1,101))
    first_name = forms.CharField(initial='John', required=False)
    last_name = forms.CharField(initial='Doe', required=False)
    clinicName = forms.CharField(required=False, label='Clinic Name')
    city = forms.CharField(initial='Burlington', required=False)
    about = forms.CharField(required=False, label='About the clinic', widget=forms.Textarea)
    province = forms.ChoiceField(choices=PROVINCES, required=False)
    username = forms.CharField(initial='loribine' + str(random.choice(x)) + '@gmail.com', label='Email')
    user_type = forms.ModelChoiceField(queryset=UserType.objects.all())
    imageOne = forms.ImageField(required=False, label='Image 1')
    imageTwo = forms.ImageField(required=False, label='Image 2')
    imageThree = forms.ImageField(required=False, label='Image 3')
    imageFour = forms.ImageField(required=False, label='Image 4')

    class Meta:
        model = User
        fields = ('user_type', 'clinicName', 'first_name', 'last_name', 'username', 'city', 'province', 'about', 'password1' ,'password2', 'imageOne', 'imageTwo', 'imageThree', 'imageFour' )

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1' ,'password2']

class UserFormClinic(forms.ModelForm):
    email = forms.EmailField()  # This For Additional Field
    class Meta:
        model = User
        # fields = ['first_name', 'last_name', 'email']
        fields = ['email']

class UserFormTherapist(forms.ModelForm):
    email = forms.EmailField()  # This For Additional Field
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileUpdateClinic(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['clinicName', 'city', 'province', 'about', 'imageOne', 'imageTwo', 'imageThree', 'imageFour', 'practiceArea']

# class ProfileUpdateTherapist(forms.ModelForm):
#     class Meta:
#         model = Account
#         fields = ['clinicName', 'city', 'province', 'about', 'imageOne', 'imageTwo', 'imageThree', 'imageFour', 'practiceArea']