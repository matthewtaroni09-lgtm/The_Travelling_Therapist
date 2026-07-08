from dataclasses import field
from datetime import datetime, timedelta
import email, re
from operator import mod
from pyexpat import model
from tkinter import Widget
from django import forms
from .models import PROVINCES, Auction, Bid, Account, Demographic, DemographicType, PracticeArea, PracticeAreaType, User, UserType, MessageAcknowledgement, PaymentType
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
import random
from django.core.exceptions import ValidationError
import os
from django.forms import inlineformset_factory

def check_times(start_time, end_time, day):
    if (start_time is None and end_time is not None) or (start_time is not None and end_time is None):
        return "Please ensure that the start and end times are completed for " + str(day) + ". If this is not a working day please remove both start and end times."
    elif start_time is not None and end_time is not None:
        if start_time >= end_time:
            return str(day) + "'s start time is after the end time."
        else:
            return ''
    elif start_time is None and end_time is None:
        return 'None'
    else: 
        return ''

def validate_clinic_fields(clinicName, city, province, username):
    error_list = []
    if clinicName == '' or clinicName is None:
        error_list.append(ValidationError("Please enter a healthcare facility name."))

    if city == '' or city is None:
        error_list.append(ValidationError("Please enter a city."))

    if province == '' or province is None:
        error_list.append(ValidationError("Please enter a province."))

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if username and not re.match(pattern, username):
        error_list.append(ValidationError("Email is not in the correct format."))

    # if underEighteen is None or eighteenToSixtyFive is None or overSixtyFive is None:
    #     error_list.append(ValidationError("Please enter a value for all Clinic Demographics. If one of the age groups does not apply put in a 0."))
    # elif underEighteen < 0 or eighteenToSixtyFive < 0 or overSixtyFive < 0:
    #     error_list.append(ValidationError("Please enter a positive value for all Clinic Demographics. If one of the age groups does not apply put in a 0."))
    # else:
    #     if (underEighteen + eighteenToSixtyFive + overSixtyFive) != 100:
    #         error_list.append(ValidationError("Clinic Demographics values must add to 100%."))

    # if MSK is None or neuro is None or cardioResp is None:
    #     error_list.append(ValidationError("Please enter a value for all Clinic Areas of Practice. If one of the areas does not apply put in a 0."))
    # elif MSK < 0 or neuro < 0 or cardioResp < 0:
    #     error_list.append(ValidationError("Please enter a positive value for all Clinic Areas of Practice. If one of the areas does not apply put in a 0."))
    # else:
    #     if (MSK + neuro + cardioResp) != 100:
    #         error_list.append(ValidationError("Clinic Areas of Practice values must add to 100%."))
    return error_list

def validate_file_extension(value, image_name): 
    error_list = []
    if value is not None and isinstance(value, bool) is not True:
        ext = os.path.splitext(value.name)[1]
        valid_extensions = ['.jpeg', '.jpg', '.png', '.heic']
        if not ext.lower() in valid_extensions:
            error_list.append(ValidationError(u'Unsupported file extension for ' + str(image_name) + '. Valid file types are' + ', '.join(valid_extensions) + '.'))

        try:
            if value.size > 10485760:
                error_list.append(ValidationError(u'Max file size exceeded for ' + str(image_name) + ', images must be less than 10 MB.'))
        except (FileNotFoundError, OSError, ValueError):
            # Existing file references can be missing on disk; do not block unrelated updates.
            pass

    return error_list


class AuctionForm(forms.ModelForm):
    paymentTypesSelection = forms.MultipleChoiceField(
        label='I would like to receive offers for',
        choices=(('Fee Split', 'Fee Split'), ('Flat Fee', 'Flat Fee')),
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )

    flatFeeType = forms.ChoiceField(
        label='I would like Flat Fee offers to be:',
        choices=(('hourly', 'Hourly'), ('total_contract', 'Total Contract Price')),
        required=False,
        widget=forms.RadioSelect,
    )

    desiredFeeSplitPercentage = forms.IntegerField(
        label='Desired fee split percentage (optional)',
        required=False,
        min_value=1,
        max_value=100,
    )

    desiredFlatFeeHourly = forms.IntegerField(
        label='Desired hourly flat fee (optional)',
        required=False,
        min_value=1,
    )

    desiredFlatFeeTotalContract = forms.IntegerField(
        label='Desired total contract flat fee (optional)',
        required=False,
        min_value=1,
    )

    class Meta:
        model = Auction
        fields = ( 
            'type',
            'placementStart', 
            'placementEnd', 
            'flatFeeType',
            'desiredFeeSplitPercentage',
            'desiredFlatFeeHourly',
            'desiredFlatFeeTotalContract',
            'treatmentCost',
            'treatmentMin',
            'assessmentCost',
            'assessmentMin',
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
        )

        widgets = {
            'placementStart': forms.DateInput(format=('%Y-%m-%d'), attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date', 'value': '2022-01-01'}),
            'placementEnd': forms.DateInput(format=('%Y-%m-%d'), attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date', 'value': '2022-01-02'}),
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
            'desiredFeeSplitPercentage': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '100', 'placeholder': 'e.g. 65'}),
            'desiredFlatFeeHourly': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'e.g. 80'}),
            'desiredFlatFeeTotalContract': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'placeholder': 'e.g. 5000'}),
            'comments': forms.Textarea(attrs={'placeholder': 'Tell us about your clinic...', 'rows': '4'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial.setdefault('paymentTypesSelection', self.instance.get_payment_types_list())
            self.initial.setdefault('flatFeeType', self.instance.flatFeeType)

    def clean(self):
        cleaned_data = super().clean()
        placementStart = cleaned_data.get('placementStart')
        placementEnd = cleaned_data.get('placementEnd')
        payment_types = cleaned_data.get('paymentTypesSelection') or []
        flat_fee_type = cleaned_data.get('flatFeeType')
        desired_fee_split_percentage = cleaned_data.get('desiredFeeSplitPercentage')
        desired_flat_fee_hourly = cleaned_data.get('desiredFlatFeeHourly')
        desired_flat_fee_total_contract = cleaned_data.get('desiredFlatFeeTotalContract')

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
        none_count = 0

        if placementStart > datetime.now().date() + timedelta(days=365):
            error_list.append(ValidationError("Placements must start within the next 12 months."))

        if placementEnd <= placementStart:
            error_list.append(ValidationError("The end of placement date must be after the start date of placement"))

        if (placementEnd - placementStart).days > 730:
            error_list.append(ValidationError("Placements must be less than two years."))

        if monday_val == 'None':
            none_count = none_count + 1
        elif monday_val != '' and monday_val != 'None':
            error_list.append(ValidationError(monday_val))

        if tuesday_val == 'None':
            none_count = none_count + 1
        elif tuesday_val != '' and tuesday_val != 'None':
            error_list.append(ValidationError(tuesday_val))

        if wednesday_val == 'None':
            none_count = none_count + 1
        if wednesday_val != '' and wednesday_val != 'None':
            error_list.append(ValidationError(wednesday_val))

        if thursday_val == 'None':
            none_count = none_count + 1
        if thursday_val != '' and thursday_val != 'None':
            error_list.append(ValidationError(thursday_val))

        if friday_val == 'None':
            none_count = none_count + 1
        if friday_val != '' and friday_val != 'None':
            error_list.append(ValidationError(friday_val))

        if saturday_val == 'None':
            none_count = none_count + 1
        if saturday_val != '' and saturday_val != 'None':
            error_list.append(ValidationError(saturday_val))

        if sunday_val == 'None':
            none_count = none_count + 1
        if sunday_val != '' and sunday_val != 'None':
            error_list.append(ValidationError(sunday_val))

        if none_count == 7:
            error_list.append(ValidationError('At least one start and end time must be entered.'))

        if len(payment_types) == 0:
            error_list.append(ValidationError('Please select at least one payment type.'))

        if 'Flat Fee' in payment_types and not flat_fee_type:
            error_list.append(ValidationError('Please select how flat fee offers should be priced.'))

        if desired_fee_split_percentage is not None and 'Fee Split' not in payment_types:
            error_list.append(ValidationError('Desired fee split guidance can only be set when Fee Split is selected.'))

        if desired_flat_fee_hourly is not None and ('Flat Fee' not in payment_types or flat_fee_type != 'hourly'):
            error_list.append(ValidationError('Desired hourly flat fee guidance can only be set when Flat Fee (Hourly) is selected.'))

        if desired_flat_fee_total_contract is not None and ('Flat Fee' not in payment_types or flat_fee_type != 'total_contract'):
            error_list.append(ValidationError('Desired total contract flat fee guidance can only be set when Flat Fee (Total Contract Price) is selected.'))

        if len(error_list) > 0:
            raise forms.ValidationError(error_list)

        return cleaned_data

    def save(self, commit=True):
        auction = super().save(commit=False)
        payment_types = self.cleaned_data.get('paymentTypesSelection') or []
        auction.paymentTypes = ','.join(payment_types)
        auction.flatFeeType = self.cleaned_data.get('flatFeeType') if 'Flat Fee' in payment_types else None

        auction.desiredFeeSplitPercentage = self.cleaned_data.get('desiredFeeSplitPercentage') if 'Fee Split' in payment_types else None
        if 'Flat Fee' in payment_types and auction.flatFeeType == 'hourly':
            auction.desiredFlatFeeHourly = self.cleaned_data.get('desiredFlatFeeHourly')
            auction.desiredFlatFeeTotalContract = None
        elif 'Flat Fee' in payment_types and auction.flatFeeType == 'total_contract':
            auction.desiredFlatFeeHourly = None
            auction.desiredFlatFeeTotalContract = self.cleaned_data.get('desiredFlatFeeTotalContract')
        else:
            auction.desiredFlatFeeHourly = None
            auction.desiredFlatFeeTotalContract = None

        primary_payment_type = payment_types[0] if payment_types else ''
        if primary_payment_type:
            payment_type = PaymentType.objects.filter(name=primary_payment_type).first()
            if payment_type is not None:
                auction.paymentType = payment_type

        if commit:
            auction.save()
            self.save_m2m()

        return auction


class AuctionAdminForm(AuctionForm):
    field_order = [
        'paymentTypes',
        'paymentTypesSelection',
        'flatFeeType',
    ]

    active = forms.BooleanField(required=False, label='Active Listing')
    closed = forms.BooleanField(required=False, label='Closed Listing')
    deleted = forms.BooleanField(required=False, label='Deleted Listing')

    class Meta(AuctionForm.Meta):
        fields = '__all__'
        exclude = ('reservePrice', 'paymentType')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.initial.setdefault('active', self.instance.active)
            self.initial.setdefault('closed', self.instance.closed)
            self.initial.setdefault('deleted', self.instance.deleted)

class BidForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.max_bid = kwargs.pop('max_bid', None)
        self.min_bid_increment = kwargs.pop('min_bid_increment', None)
        self.payment_type = kwargs.pop('payment_type', None)
        super(BidForm, self).__init__(*args, **kwargs)
    amount = forms.IntegerField(min_value=0, max_value=100000, required=False)
    class Meta:
        model = Bid
        fields = ('amount', )

    # This should be caught in JS validations but keep this here in case the user tries to get around front-end validations 
    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is None:
            raise forms.ValidationError("Please enter an offer amount.")

        amount_delta = amount - self.max_bid if self.max_bid is not None else 'N/A'
        print(str(amount) + "  " + str(self.max_bid) + "  " + str(self.min_bid_increment) + "  " + str(amount_delta))
        print("less than: " + str(self.max_bid) + " || " + "greater than " + str(self.max_bid) + str(self.min_bid_increment) + " ")
        if self.payment_type == 'Flat Fee' and self.max_bid is not None and self.min_bid_increment is not None and amount < self.max_bid and amount > self.max_bid + self.min_bid_increment:
            raise forms.ValidationError("Bids must be less than the next bid increment  $" + str(self.min_bid_increment) + ".")
        if amount == 0:
            if self.payment_type == 'Fee Split':
                raise forms.ValidationError("Bids must be greater than 0%.")
            else:
                raise forms.ValidationError("Bids must be greater than $0.")
        if amount > 100 and self.payment_type == 'Fee Split':
                raise forms.ValidationError("Bids must be less than 100%.")
        return amount 

class RegisterAcount(UserCreationForm):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    clinicName = forms.CharField(required=False, label='Healthcare facility Name')
    city = forms.CharField(required=False)
    about = forms.CharField(required=False, label='About the healthcare facility', widget=forms.Textarea)
    province = forms.ChoiceField(choices=PROVINCES, required=False)
    username = forms.CharField(label='Email')
    user_type = forms.ModelChoiceField(queryset=UserType.objects.all())
    imageOne = forms.ImageField(required=False, label='Image 1')
    imageTwo = forms.ImageField(required=False, label='Image 2')
    imageThree = forms.ImageField(required=False, label='Image 3')
    imageFour = forms.ImageField(required=False, label='Image 4')

    class Meta:
        model = User
        fields = ('user_type', 'clinicName', 'first_name', 'last_name', 'username', 'city', 'province', 'about', 'password1' ,'password2', 'imageOne', 'imageTwo', 'imageThree', 'imageFour')

    def clean(self):
        userType = self.cleaned_data.get('user_type')
        firstName = self.cleaned_data.get('first_name')
        lastName = self.cleaned_data.get('last_name')
        clinicName = self.cleaned_data.get('clinicName')
        city = self.cleaned_data.get('city')
        about = self.cleaned_data.get('about')
        province = self.cleaned_data.get('province')
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        imageOne = self.cleaned_data.get('imageOne')
        imageTwo = self.cleaned_data.get('imageTwo')
        imageThree = self.cleaned_data.get('imageThree')
        imageFour = self.cleaned_data.get('imageFour')

        # If the username is none it is a duplicate that Django has already caught and removed. Returning here triggers the front-end error message to be displayed
        if username is None:
            return

        error_list = []

        image_errors_one = validate_file_extension(imageOne, 'Clinic Image One')
        image_errors_two = validate_file_extension(imageTwo, 'Clinic Image Two')
        image_errors_three = validate_file_extension(imageThree, 'Clinic Image Three')
        image_errors_four = validate_file_extension(imageFour, 'Clinic Image Four')

        if image_errors_one is not None:
            error_list.extend(image_errors_one)
        if image_errors_two is not None:
            error_list.extend(image_errors_two)
        if image_errors_three is not None:
            error_list.extend(image_errors_three)
        if image_errors_four is not None:
            error_list.extend(image_errors_four)

        if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
            error_list.append(f'Username "{username}" is already in use.')
            print(f'Username "{username}" is already in use.')

        if str(userType).split(' ')[-1] == "Clinic":
            errors = validate_clinic_fields(clinicName, city, province, username)
            if errors is not None:
                error_list.extend(errors)

            if len(clinicName) <= 4:
                error_list.append(ValidationError("Please enter a healthcare facility name that is greater than 4 characters."))
        else:
            if firstName == '' or firstName is None:
                error_list.append(ValidationError("Please enter a first name."))
            elif any(char.isdigit() for char in firstName):
                error_list.append(ValidationError("First name cannot contain numbers."))

            if firstName is not None and len(firstName) <= 1:
                error_list.append(ValidationError("Please enter a first name that is greater than 1 character."))

            if lastName == '' or lastName is None:
                error_list.append(ValidationError("Please enter a last name."))
            elif any(char.isdigit() for char in lastName):
                error_list.append(ValidationError("Last name cannot contain numbers."))

            if lastName is not None and len(lastName) <= 1:
                error_list.append(ValidationError("Please enter a last name that is greater than 1 character."))

            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, username):
                error_list.append(ValidationError("Email is not in the correct format."))

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
        email = self.cleaned_data.get('email')

        error_list = []

        if User.objects.exclude(pk=self.instance.pk).filter(username=email).exists():
            error_list.append(f'Username "{email}" is already in use.')

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            error_list.append(ValidationError("Email is not in the correct format."))

        if email == '' or email is None:
            error_list.append(ValidationError("Please enter a properly formatted email."))

        if len(error_list) > 0:
            raise forms.ValidationError(error_list)

class UserFormTherapist(forms.ModelForm):
    # user_email = forms.EmailField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def clean(self):
        firstName = self.cleaned_data.get('first_name')
        lastName = self.cleaned_data.get('last_name')
        email = self.cleaned_data.get('email')
        print("!!UserFormTherapist!!")
        print(email)
        error_list = []

        if User.objects.exclude(pk=self.instance.pk).filter(username=email).exists():
            error_list.append(f'Username "{email}" is already in use.')

        if firstName == '' or firstName is None:
            error_list.append(ValidationError("First name cannot be blank."))
        elif any(char.isdigit() for char in firstName):
            error_list.append(ValidationError("First name cannot contain numbers."))

        if lastName == '' or lastName is None:
            error_list.append(ValidationError("Last name cannot be blank."))
        elif any(char.isdigit() for char in lastName):
            error_list.append(ValidationError("Last name cannot contain numbers."))

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            error_list.append(ValidationError("Email is not in the correct format."))

        if len(error_list) > 0:
            raise forms.ValidationError(error_list)

class ProfileUpdateClinic(forms.ModelForm):
    # underEighteen = forms.IntegerField(required=False, label='% Under 18', min_value=0, max_value=100)
    # eighteenToSixtyFive = forms.IntegerField(required=False, label='% 18 - 65', min_value=0, max_value=100)
    # overSixtyFive = forms.IntegerField(required=False, label='% Over 65', min_value=0, max_value=100)
    # MSK = forms.IntegerField(required=False, label='% Musculoskeletal', min_value=0, max_value=100)
    # neuro = forms.IntegerField(required=False, label='% Neurological', min_value=0, max_value=100)
    # cardioResp = forms.IntegerField(required=False, label='% Cardiorespiratory', min_value=0, max_value=100)
    
    class Meta:
        model = Account
        fields = ['clinicName', 'city', 'province', 'about', 'imageOne', 'imageTwo', 'imageThree', 'imageFour']

    def clean(self):
        clinicName = self.cleaned_data.get('clinicName')
        city = self.cleaned_data.get('city')
        about = self.cleaned_data.get('about')
        province = self.cleaned_data.get('province')
        username = self.instance.user.username if getattr(self.instance, 'user', None) else None
        imageOne = self.cleaned_data.get('imageOne')
        imageTwo = self.cleaned_data.get('imageTwo')
        imageThree = self.cleaned_data.get('imageThree')
        imageFour = self.cleaned_data.get('imageFour')
        # underEighteen = self.cleaned_data.get('underEighteen')
        # eighteenToSixtyFive = self.cleaned_data.get('eighteenToSixtyFive')
        # overSixtyFive = self.cleaned_data.get('overSixtyFive')
        # MSK = self.cleaned_data.get('MSK')
        # neuro = self.cleaned_data.get('neuro')
        # cardioResp = self.cleaned_data.get('cardioResp')

        error_list = []

        image_errors_one = validate_file_extension(imageOne, 'Clinic Image One')
        image_errors_two = validate_file_extension(imageTwo, 'Clinic Image Two')
        image_errors_three = validate_file_extension(imageThree, 'Clinic Image Three')
        image_errors_four = validate_file_extension(imageFour, 'Clinic Image Four')

        if image_errors_one is not None:
            error_list.extend(image_errors_one)
        if image_errors_two is not None:
            error_list.extend(image_errors_two)
        if image_errors_three is not None:
            error_list.extend(image_errors_three)
        if image_errors_four is not None:
            error_list.extend(image_errors_four)

        errors = validate_clinic_fields(clinicName, city, province, username)
        if errors is not None:
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

class DemographicForm(forms.ModelForm):
    class Meta:
        model = Demographic
        fields = ['category', 'percentage']

    def clean(self):
        percentage = self.cleaned_data.get('percentage')
        error_list = []
        if percentage > 100:
            error_list.append(ValidationError("Each demographic bust be less than 100%."))

        if len(error_list) > 0:
            raise forms.ValidationError(error_list)

class PracticeAreaForm(forms.ModelForm):
    class Meta:
        model = PracticeArea
        fields = ['category', 'percentage']

    def __init__(self, *arg, **kwarg):
        super(PracticeAreaForm, self).__init__(*arg, **kwarg)
        self.empty_permitted = True

    def clean(self):
        percentage = self.cleaned_data.get('percentage')
        error_list = []

        # If percentage is None the user has not entered a value so the validation can be skipped
        if percentage is not None:
            if percentage > 100:
                error_list.append(ValidationError("Each area of practice must be less than 100%."))

            if len(error_list) > 0:
                raise forms.ValidationError(error_list)

class AuctionAccountForm(forms.ModelForm):
    remember_auction_data = forms.BooleanField(required=False, label="Remember listing information for next time?")

    class Meta:
        model = Account
        fields = ['remember_auction_data']

class MessageAcknowledgementForm(forms.ModelForm):
    acknowledged = forms.BooleanField(required=False, label="Remember listing information for next time?")

    class Meta:
        model = MessageAcknowledgement
        fields = ['acknowledged']

