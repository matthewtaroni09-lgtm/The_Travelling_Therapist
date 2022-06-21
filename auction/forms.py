from datetime import datetime, timedelta
import email
from operator import mod
from pyexpat import model
from tkinter import Widget
from django import forms
from .models import PROVINCES, Auction, Bid, Account, Demographic, User, UserType
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
import random
from django.core.exceptions import ValidationError

def check_times(start_time, end_time, day):
    if (start_time is None and end_time is not None) or (start_time is not None and end_time is None):
        return "Please ensure that the start and end times are completed for " + str(day) + ". If this is not a working day please remove both start and end times."
    elif start_time is not None and end_time is not None:
        if start_time >= end_time:
            return str(day) + "'s start time is after the end time."
        else:
            return ''
    else: 
        return ''

def validate_clinic_fields(clinicName, city, province, underEighteen, eighteenToSixtyFive, overSixtyFive, MSK, neuro, cardioResp):
    error_list = []
    if clinicName == '' or clinicName is None:
        error_list.append(ValidationError("Please enter a clinic name."))

    if city == '' or city is None:
        error_list.append(ValidationError("Please enter a city."))

    if province == '' or province is None:
        error_list.append(ValidationError("Please enter a province."))

    if underEighteen is None or eighteenToSixtyFive is None or overSixtyFive is None:
        error_list.append(ValidationError("Please enter a value for all Clinic Demographics. If one of the age groups does not apply put in a 0."))
    else:
        if (underEighteen + eighteenToSixtyFive + overSixtyFive) != 100:
            error_list.append(ValidationError("Clinic Demographics values must add to 100%."))

    if MSK is None or neuro is None or cardioResp is None:
        error_list.append(ValidationError("Please enter a value for all Clinic Areas of Practice. If one of the age groups does not apply put in a 0."))
    else:
        if (MSK + neuro + cardioResp) != 100:
            error_list.append(ValidationError("Clinic Areas of Practice values must add to 100%."))
    print("val_clinic_fields"+str(error_list))
    return error_list
        

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

    def clean(self):
        placementStart = self.cleaned_data.get('placementStart')
        placementEnd = self.cleaned_data.get('placementEnd')
        reservePrice = self.cleaned_data.get('reservePrice')

        mondayStart = self.cleaned_data.get('mondayStart')
        mondayEnd = self.cleaned_data.get('mondayEnd')
        tuesdayStart = self.cleaned_data.get('tuesdayStart')
        tuesdayEnd = self.cleaned_data.get('tuesdayEnd')
        wednesdayStart = self.cleaned_data.get('wednesdayStart')
        wednesdayEnd = self.cleaned_data.get('wednesdayEnd')
        thursdayStart = self.cleaned_data.get('thursdayStart')
        thursdayEnd = self.cleaned_data.get('thursdayEnd')
        fridayStart = self.cleaned_data.get('fridayStart')
        fridayEnd = self.cleaned_data.get('fridayEnd')
        saturdayStart = self.cleaned_data.get('saturdayStart')
        saturdayEnd = self.cleaned_data.get('saturdayEnd')
        sundayStart = self.cleaned_data.get('sundayStart')
        sundayEnd = self.cleaned_data.get('sundayEnd')

        monday_val = check_times(mondayStart, mondayEnd, 'Monday')
        tuesday_val = check_times(tuesdayStart, tuesdayEnd, 'Tuesday')
        wednesday_val = check_times(wednesdayStart, wednesdayEnd, 'Wednesday')
        thursday_val = check_times(thursdayStart, thursdayEnd, 'Thursday')
        friday_val = check_times(fridayStart, fridayEnd, 'Friday')
        saturday_val = check_times(saturdayStart, saturdayEnd, 'Saturday')
        sunday_val = check_times(sundayStart, sundayEnd, 'Sunday')

        error_list = []
        if placementStart > datetime.now().date() + timedelta(days=365):
            error_list.append(ValidationError("Placements must start within the next 12 months."))

        if reservePrice is not None:
            if reservePrice < 0:
                error_list.append(ValidationError("Reserve price cannot be 0 or less. If no reserve price is desired leave the field blank."))

        if reservePrice is not None:
            if reservePrice > 25000:
                error_list.append(ValidationError("Reserve price must be less than $25,000."))

        if placementEnd <= placementStart:
            error_list.append(ValidationError("The end of placement date must be before the start of placement."))

        if (placementEnd - placementStart).days > 730:
            error_list.append(ValidationError("Placements must be less than two years."))

        if monday_val != '':
            error_list.append(ValidationError(monday_val))
        if tuesday_val != '':
            error_list.append(ValidationError(tuesday_val))
        if wednesday_val != '':
            error_list.append(ValidationError(wednesday_val))
        if thursday_val != '':
            error_list.append(ValidationError(thursday_val))
        if friday_val != '':
            error_list.append(ValidationError(friday_val))
        if saturday_val != '':
            error_list.append(ValidationError(saturday_val))
        if sunday_val != '':
            error_list.append(ValidationError(sunday_val))

        if len(error_list) > 0:
            raise forms.ValidationError(error_list)

class BidForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.max_bid = kwargs.pop('max_bid', None)
        self.min_bid_increment = kwargs.pop('min_bid_increment', None)
        super(BidForm, self).__init__(*args, **kwargs)

    amount = forms.IntegerField(max_value=100000, min_value=0)
    class Meta:
        model = Bid
        fields = ('amount', )

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount > 0 and self.max_bid > 0 and amount % self.min_bid_increment != 0:
            raise forms.ValidationError("Bids must be in increments of $" + str(self.min_bid_increment) + ".")
        return amount 

class RegisterAcount(UserCreationForm):
    first_name = forms.CharField(required=False)
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
    underEighteen = forms.IntegerField(required=False, label='% Under 18')
    eighteenToSixtyFive = forms.IntegerField(required=False, label='% 18 - 65')
    overSixtyFive = forms.IntegerField(required=False, label='% Over 65')
    MSK = forms.IntegerField(required=False, label='% Musculoskeletal')
    neuro = forms.IntegerField(required=False, label='% Neurological')
    cardioResp = forms.IntegerField(required=False, label='% Cardiorespiratory')

    class Meta:
        model = User
        fields = ('user_type', 'clinicName', 'first_name', 'last_name', 'username', 'city', 'province', 'about', 'underEighteen', 'eighteenToSixtyFive', 'overSixtyFive', 'MSK', 'neuro', 'cardioResp', 'password1' ,'password2', 'imageOne', 'imageTwo', 'imageThree', 'imageFour')

    def clean(self):
        userType = self.cleaned_data.get('user_type')
        firstName = self.cleaned_data.get('first_name')
        lastName = self.cleaned_data.get('last_name')
        clinicName = self.cleaned_data.get('clinicName')
        city = self.cleaned_data.get('city')
        about = self.cleaned_data.get('about')
        province = self.cleaned_data.get('province')
        username = self.cleaned_data.get('username')
        imageOne = self.cleaned_data.get('imageOne')
        imageTwo = self.cleaned_data.get('imageTwo')
        imageThree = self.cleaned_data.get('imageThree')
        imageFour = self.cleaned_data.get('imageFour')
        underEighteen = self.cleaned_data.get('underEighteen')
        eighteenToSixtyFive = self.cleaned_data.get('eighteenToSixtyFive')
        overSixtyFive = self.cleaned_data.get('overSixtyFive')
        MSK = self.cleaned_data.get('MSK')
        neuro = self.cleaned_data.get('neuro')
        cardioResp = self.cleaned_data.get('cardioResp')

        error_list = []

        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            error_list.append(f'Username "{username}" is already in use.')

        if str(userType).split(' ')[-1] == "Clinic":
            errors = validate_clinic_fields(clinicName, city, province, underEighteen, eighteenToSixtyFive, overSixtyFive, MSK, neuro, cardioResp)
            if errors != None:
                error_list.extend(errors)
        else:
            if firstName == '' or firstName is None:
                error_list.append(ValidationError("Please enter a first name."))

            if lastName == '' or lastName is None:
                error_list.append(ValidationError("Please enter a last name."))

        if len(error_list) > 0:
            raise forms.ValidationError(error_list)

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1' ,'password2']

class UserFormClinic(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['email']
    
    def clean(self):
        print("in user")
        email = self.cleaned_data.get('email')

        error_list = []

        if User.objects.exclude(pk=self.instance.pk).filter(username=email).exists():
            error_list.append(f'Username "{email}" is already in use.')

        if email == '' or email is None:
            error_list.append(ValidationError("Please enter a properly formatted email."))

        if len(error_list) > 0:
            raise forms.ValidationError(error_list)

class UserFormTherapist(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def clean(self):
        firstName = self.cleaned_data.get('first_name')
        lastName = self.cleaned_data.get('last_name')
        email = self.cleaned_data.get('email')

        error_list = []

        if User.objects.exclude(pk=self.instance.pk).filter(username=email).exists():
            error_list.append(f'Username "{email}" is already in use.')

        if firstName == '' or firstName is None:
            error_list.append(ValidationError("First name cannot be blank."))

        if lastName == '' or lastName is None:
            error_list.append(ValidationError("Last name cannot be blank."))

        if len(error_list) > 0:
            raise forms.ValidationError(error_list)

class ProfileUpdateClinic(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['clinicName', 'city', 'province', 'about', 'underEighteen', 'eighteenToSixtyFive', 'overSixtyFive', 'MSK', 'neuro', 'cardioResp', 'imageOne', 'imageTwo', 'imageThree', 'imageFour']

    def clean(self):
        print("in vals")
        clinicName = self.cleaned_data.get('clinicName')
        city = self.cleaned_data.get('city')
        about = self.cleaned_data.get('about')
        province = self.cleaned_data.get('province')
        username = self.cleaned_data.get('username')
        imageOne = self.cleaned_data.get('imageOne')
        imageTwo = self.cleaned_data.get('imageTwo')
        imageThree = self.cleaned_data.get('imageThree')
        imageFour = self.cleaned_data.get('imageFour')
        underEighteen = self.cleaned_data.get('underEighteen')
        eighteenToSixtyFive = self.cleaned_data.get('eighteenToSixtyFive')
        overSixtyFive = self.cleaned_data.get('overSixtyFive')
        MSK = self.cleaned_data.get('MSK')
        neuro = self.cleaned_data.get('neuro')
        cardioResp = self.cleaned_data.get('cardioResp')

        error_list = []

        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            error_list.append(f'Username "{username}" is already in use.')

        errors = validate_clinic_fields(clinicName, city, province, underEighteen, eighteenToSixtyFive, overSixtyFive, MSK, neuro, cardioResp)
        if errors != None:
            error_list.extend(errors)
    
        if len(error_list) > 0:
            raise forms.ValidationError(error_list)

class PasswordChangingForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
    new_password1 = forms.CharField(label='Enter new password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))
    new_password2 = forms.CharField(label='Re-enter new password', widget=forms.PasswordInput(attrs={'class': 'form-control', 'type': 'password'}))

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')

class ContactForm(forms.Form):
    first_name = forms.CharField(max_length = 50)
    last_name = forms.CharField(max_length = 50)
    email_address = forms.EmailField(max_length = 150)
    message = forms.CharField(widget = forms.Textarea, max_length = 2000)

class testForm(forms.Form):
    name = forms.CharField(label="New Pay Frequency", max_length=100, widget=forms.TextInput(attrs={'class': 'input'}))

    def clean_name(self):
        data = self.cleaned_data.get('name')

        if 'aa' not in data:
            raise forms.ValidationError('No aa')
        return data