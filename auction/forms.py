import email
from operator import mod
from pyexpat import model
from tkinter import Widget
from django import forms
from .models import PROVINCES, Auction, Bid, Account, Demographic, User, UserType
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
import random
from django.core.exceptions import ValidationError

class AuctionForm(forms.ModelForm):
    reservePrice = forms.IntegerField(max_value=25000, min_value=1)
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

    # def clean(self):
    #     reservePrice = self.cleaned_data.get('reservePrice')
    #     print(reservePrice)
    #     if reservePrice > 50:
            
    #         raise forms.ValidationError("Mx  50")
    #     return reservePrice

class BidForm(forms.ModelForm):
    amount = forms.IntegerField(max_value=25000, min_value=1)
    class Meta:
        model = Bid
        fields = ('amount', )

    # def clean_amount(self):
    #     email_passed = self.cleaned_data.get("amount")
    #     if not email_passed > 50:
    #         raise forms.ValidationError("Sorry, the email submitted is invalid. All emails have to be registered on this domain only.")
    #     return email_passed

class RegisterAcount(UserCreationForm):
    first_name = forms.CharField( required=False)
    last_name = forms.CharField(required=False)
    clinicName = forms.CharField(required=False, label='Clinic Name')
    city = forms.CharField(required=False)
    about = forms.CharField(required=False, label='About the clinic', widget=forms.Textarea)
    province = forms.ChoiceField(choices=PROVINCES, required=False)
    username = forms.CharField(label='Email')
    user_type = forms.ModelChoiceField(queryset=UserType.objects.all())
    imageOne = forms.ImageField(required=False, label='Image 1')
    imageTwo = forms.ImageField(required=False, label='Image 2')
    imageThree = forms.ImageField(required=False, label='Image 3')
    imageFour = forms.ImageField(required=False, label='Image 4')
    underEighteen = forms.IntegerField(required=False, label='Under 18')
    eighteenToSixtyFive = forms.IntegerField(required=False, label='18 - 65')
    overSixtyFive = forms.IntegerField(required=False, label='Over 65')
    MSK = forms.IntegerField(required=False, label='Musculoskeletal')
    neuro = forms.IntegerField(required=False, label='Neurological')
    cardioResp = forms.IntegerField(required=False, label='Cardiorespiratory')

    class Meta:
        model = User
        fields = ('user_type', 'clinicName', 'first_name', 'last_name', 'username', 'city', 'province', 'about', 'underEighteen', 'eighteenToSixtyFive', 'overSixtyFive', 'MSK', 'neuro', 'cardioResp', 'password1' ,'password2', 'imageOne', 'imageTwo', 'imageThree', 'imageFour')

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
        fields = ['clinicName', 'city', 'province', 'about', 'underEighteen', 'eighteenToSixtyFive', 'overSixtyFive', 'MSK', 'neuro', 'cardioResp', 'imageOne', 'imageTwo', 'imageThree', 'imageFour']

class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
    new_password1 = forms.CharField(label='Enter new password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
    new_password2 = forms.CharField(label='Re-enter new password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')