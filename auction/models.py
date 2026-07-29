import pytz
from django.utils import timezone as django_timezone
import datetime
import math
import os
import re
from tabnanny import verbose
from unicodedata import category
from urllib.parse import parse_qs, urlparse
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import uuid
from django.utils.deconstruct import deconstructible
from uuid import uuid4

from django.dispatch import receiver

PROVINCES = (
    ("", "----------"),
    ("Alberta", "Alberta"),
    ("British Columbia", "British Columbia"),
    ("Manitoba", "Manitoba"),
    ("New Brunswick", "New Brunswick"),
    ("Newfoundland and Labrador", "Newfoundland and Labrador"),
    ("Nova Scotia", "Nova Scotia"),
    ("Ontario", "Ontario"),
    ("Prince Edward Island", "Prince Edward Island"),
    ("Quebec", "Quebec"),
    ("Saskatchewan", "Saskatchewan"),
    ("Northwest Territories", "Northwest Territories"),
    ("Nunavut", "Nunavut"), 
    ("Yukon", "Yukon"),
)

PAYMENT_TYPE_CHOICES = (
    ('Fee Split', 'Fee Split'),
    ('Flat Fee', 'Flat Fee'),
)

LISTING_SKILL_OPTIONS = [
    'Private clinic experience',
    'Ability to work independently',
    'Experience with specific treatments/modalities',
    'Strong communication/interpersonal skills',
    'Documentation and EMR proficiency',
    'Previous experience in a similar role',
]

PROFILE_SKILL_OPTIONS = [
    'Private clinic experience',
    'Ability to work independently',
    'Experience with specific treatments/modalities',
    'Strong communication/interpersonal skills',
    'Documentation and EMR proficiency',
]

DEFAULT_SKILL_OPTIONS = PROFILE_SKILL_OPTIONS

FLAT_FEE_TYPE_CHOICES = (
    ('hourly', 'Hourly'),
    ('total_contract', 'Total Contract Price'),
)

PAYMENT_METHOD_CHOICES = (
    ('Cash', 'Cash'),
    ('Cheque', 'Cheque'),
    ('Direct Deposit', 'Direct Deposit'),
    ('E-Transfer', 'E-Transfer'),
    ('As part of payroll with other staff', 'As part of payroll with other staff'),
    ('Other', 'Other'),
    ("Clinician's Choice", "Clinician's Choice"),
)


def normalize_youtube_embed_url(raw_url):
    if raw_url is None:
        return ''

    normalized_value = str(raw_url).strip()
    if normalized_value == '':
        return ''

    if '://' not in normalized_value:
        normalized_value = f'https://{normalized_value}'

    try:
        parsed = urlparse(normalized_value)
    except Exception:
        return None

    hostname = (parsed.netloc or '').lower()
    if hostname.startswith('www.'):
        hostname = hostname[4:]

    path = (parsed.path or '').strip('/')
    query_params = parse_qs(parsed.query or '')
    video_id = ''

    if hostname in ('youtube.com', 'm.youtube.com'):
        if path == 'watch':
            video_id = query_params.get('v', [''])[0]
        elif path.startswith('embed/'):
            video_id = path.split('/', 1)[1].split('/')[0]
        elif path.startswith('shorts/'):
            video_id = path.split('/', 1)[1].split('/')[0]
    elif hostname == 'youtu.be':
        video_id = path.split('/')[0]
    elif hostname == 'youtube-nocookie.com' and path.startswith('embed/'):
        video_id = path.split('/', 1)[1].split('/')[0]
    else:
        return None

    if not re.fullmatch(r'[A-Za-z0-9_-]{11}', video_id or ''):
        return None

    return f'https://www.youtube.com/embed/{video_id}'

@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)
path_and_rename = PathAndRename("images/")

class UserType(models.Model):
    name = models.CharField(verbose_name='Therapist Type', max_length=200, help_text='Select a therapist type')
    feeSplit = models.BooleanField(verbose_name='Allowed Fee Split', help_text='If checked this user type will be allowed to select fee split as a payment type.', default=False)

    def __str__(self):
        return self.name

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    clinicName = models.CharField(verbose_name='Clinic Name', max_length=200, blank=True, null=True, help_text='Enter the healthcare facility name.')
    userType = models.ForeignKey(UserType, verbose_name='User Type', blank=True, null=True, related_name='usertypes', on_delete=models.CASCADE)  
    licenseNumber = models.CharField(verbose_name='License Number', max_length=120, null=True, blank=True, help_text='Enter you license number.')
    imageOne = models.ImageField(default='default.jpg', verbose_name='Clinic Image One', upload_to=path_and_rename, blank=True, null=True, help_text='Upload an image (optional).')
    imageTwo = models.ImageField(verbose_name='Clinic Image Two', upload_to=path_and_rename, blank=True, null=True, help_text='Upload an image (optional).')
    imageThree = models.ImageField(verbose_name='Clinic Image Three', upload_to=path_and_rename, blank=True, null=True, help_text='Upload an image (optional).')
    imageFour = models.ImageField(verbose_name='Clinic Image Four', upload_to=path_and_rename, blank=True, null=True, help_text='Upload an image (optional).')
    city = models.CharField(verbose_name='City', max_length=120, blank=True, null=True, help_text='Enter the city your healthcare facility is in.')
    country = models.CharField(verbose_name='Conutry', max_length=100, blank=True, null=True, help_text='Enter the country your healthcare facility is in.')
    province = models.CharField(verbose_name='Province', help_text='The province the healthcare facility resides in.', blank=True, null=True, max_length=30, choices=PROVINCES)
    about = models.TextField(verbose_name='About the healthcare facility', blank=True, null=True, help_text='Tell us about your healthcare facility.')
    clinicWebsite = models.URLField(
        verbose_name='Clinic Website',
        blank=True,
        null=True,
        help_text='This field is optional. Adding a website may give more traction to your listing - your website will be linked in your listings.'
    )
    clinicVideo = models.URLField(verbose_name='Clinic Video', blank=True, null=True, help_text='This field is optional. Add a YouTube video URL to showcase your clinic.')
    underEighteen = models.IntegerField(verbose_name='% Under 18', blank=True, null=True)
    eighteenToSixtyFive = models.IntegerField(verbose_name='% 18 - 65', blank=True, null=True)
    overSixtyFive = models.IntegerField(verbose_name='% Over 65', blank=True, null=True)
    MSK = models.IntegerField(verbose_name='% Musculoskeletal', blank=True, null=True)
    neuro = models.IntegerField(verbose_name='% Neurological', blank=True, null=True)
    cardioResp = models.IntegerField(verbose_name='% Cardiorespiratory', blank=True, null=True)
    practiceArea = models.ManyToManyField('PracticeArea', blank=True)
    demographic = models.ManyToManyField('Demographic', blank=True)
    pro = models.BooleanField(verbose_name='Pro Member', null=True, blank=True)
    remember_auction_data = models.BooleanField(verbose_name='Do you want your data to be pre-populated for your next listing?', null=True, blank=True)
    auction_message_displayed = models.BooleanField(verbose_name='Listing Message Displayed', null=True, blank=True)
    numTickets = models.IntegerField(default=0, verbose_name='# of Tickets', help_text='The number of raffle tickets assigned to a user')
    last_ticket_award_date = models.DateField(null=True, blank=True, verbose_name='Last Ticket Award Date')
    
    # Referral fields
    referral_code = models.CharField(max_length=12, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals_made')
    clinicianSkills = models.JSONField(verbose_name='Clinician Skills', blank=True, null=True, default=list)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        normalized_video = normalize_youtube_embed_url(self.clinicVideo)
        if normalized_video:
            self.clinicVideo = normalized_video
        super().save(*args, **kwargs)

    @property
    def total_tickets(self):
        """Calculate total tickets from the RaffleTicket ledger."""
        from django.db.models import Sum
        return RaffleTicket.objects.filter(user=self.user).aggregate(Sum('amount'))['amount__sum'] or 0

    def add_tickets(self, amount, reason):
        """Utility to add tickets via the ledger and sync numTickets."""
        from django.db.models import F
        RaffleTicket.objects.create(user=self.user, amount=amount, reason=reason)
        # Atomically update the current numTickets value to preserve manual admin edits
        Account.objects.filter(pk=self.pk).update(numTickets=F('numTickets') + amount)
        self.refresh_from_db(fields=['numTickets'])

    @receiver(post_save, sender=User)
    def update_profile_signal(sender, instance, created, **kwargs):
        print("inside update profile")
        if created:
            import string
            import random
            
            # Generate unique referral code
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            while Account.objects.filter(referral_code=code).exists():
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            account = Account.objects.create(user=instance, numTickets=5, referral_code=code)
            # Add initial signup tickets to ledger
            RaffleTicket.objects.create(user=instance, amount=5, reason="Signup reward")
        else:
            instance.account.save()

    def check_and_award_referral(self):
        """
        Verification Gate: Award 10 tickets to the referrer after the referred user 
        is verified (completes profile or other meaningful action).
        """
        # Check if this account was referred by someone
        try:
            referral = Referral.objects.get(referred_user=self.user, status='pending')
            
            # Meaningful action: profile completion or initial signup
            # Verification logic: 
            # - For Clinics: 'clinicName' is enough (provided at registration)
            # - For others: 'first_name' is enough (provided at registration)
            is_clinic = str(self.userType).split(' ')[-1] == "Clinic"
            
            if (is_clinic and self.clinicName) or (not is_clinic and self.user.first_name):
                referral.status = 'verified'
                referral.verified_at = django_timezone.now()
                referral.save()
                
                # Award 10 tickets to the referrer
                referrer_account = referral.referrer.account
                referrer_account.add_tickets(10, f"Referral rewardy for {self.user.username}")
                print(f"Referral: Awarded 10 tickets to {referral.referrer.username} for referring {self.user.username}")

                # Send referral success email
                from django.core.mail import send_mail
                from django.conf import settings
                from . import emails
                
                # Fallback for referred facility name
                new_facility_name = self.clinicName if self.clinicName else f"{self.user.first_name} {self.user.last_name}".strip()
                if not new_facility_name:
                    new_facility_name = self.user.username
                
                # Fallback for referrer name in the greeting
                referrer_name = referral.referrer.first_name if referral.referrer.first_name else ""
                if not referrer_name and hasattr(referral.referrer, 'account'):
                    referrer_name = referral.referrer.account.clinicName
                if not referrer_name:
                    referrer_name = referral.referrer.username

                account_url = f"{settings.ACTIVE_LINK}/profile#raffles"
                
                try:
                    send_mail(
                        subject=f"You earned 10 tickets! a new facility signed up with your referral",
                        message="",
                        html_message=emails.referral_success_email(
                            referrer_name, 
                            new_facility_name, 
                            10, 
                            account_url
                        ),
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[referral.referrer.email]
                    )
                    # Admin copy
                    send_mail(
                        subject=f"**ADMIN COPY** Referral Success: {referral.referrer.username} referred {self.user.username}",
                        message=f"Referrer: {referral.referrer.username}\nNew User: {self.user.username}\nTickets Awarded: 10",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=['info@travelingtherapist.ca']
                    )
                except Exception as e:
                    print(f"Error sending referral email: {e}")

                return True
        except Referral.DoesNotExist:
            pass
        return False

    def get_referral_link(self):
        """Generate a shareable referral link."""
        from django.conf import settings
        domain = getattr(settings, 'ACTIVE_LINK', 'http://127.0.0.1:8000')
        return f"{domain}/register?ref={self.referral_code}"

    def get_successful_referrals_count(self):
        """Count of users who were referred by this user and have completed verification."""
        return Referral.objects.filter(referrer=self.user, status='verified').count()

    def get_split_user_type(self):
        return str(self.userType).split(' ')[-1]

    def get_clinician_skill_names(self):
        skills = self.clinicianSkills or []
        names = []
        for skill in skills:
            if isinstance(skill, str):
                names.append(skill)
            elif isinstance(skill, dict):
                name = (skill.get('name') or '').strip()
                selected = bool(skill.get('selected', True))
                if name and selected:
                    names.append(name)
        return names

class Referral(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
    )
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral_records')
    referred_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='referred_record')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.referrer.username} referred {self.referred_user.username} ({self.status})"

class RaffleTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_ledger')
    amount = models.IntegerField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.reason}"

class PaymentType(models.Model):
    name = models.CharField(verbose_name='Payment Type', max_length=200, help_text='Select a payment type from the list.')

    def __str__(self):
        return str(self.name)

def get_default_start_date():
    return datetime.date.today() + datetime.timedelta(days=1)

def get_default_end_date():
    return datetime.date.today() + datetime.timedelta(days=30)


class Auction(models.Model):
    auctionID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Account, related_name='auction_clinic', on_delete=models.CASCADE)
    auctionStart = models.DateTimeField(verbose_name='Auction Start', help_text='Enter the start date of the listing.')
    auctionEnd = models.DateTimeField(verbose_name='Auction End', help_text='Enter the end date of the listing.')
    placementStart = models.DateField(verbose_name='Clinican Start Date', help_text='Enter the start date of the placement.', default=get_default_start_date)
    placementEnd = models.DateField(verbose_name='Clinican End Date', help_text='Enter the end date of the placement.', default=get_default_end_date)
    mondayStart = models.TimeField(verbose_name='Start Time', null=True, blank=True, default='09:00')
    mondayEnd = models.TimeField(verbose_name='End Time', null=True, blank=True, default='17:00')
    tuesdayStart = models.TimeField(verbose_name='Start Time', null=True, blank=True, default='09:00')
    tuesdayEnd = models.TimeField(verbose_name='End Time', null=True, blank=True, default='17:00')
    wednesdayStart = models.TimeField(verbose_name='Start Time', null=True, blank=True, default='09:00')
    wednesdayEnd = models.TimeField(verbose_name='End Time', null=True, blank=True, default='17:00')
    thursdayStart = models.TimeField(verbose_name='Start Time', null=True, blank=True, default='09:00')
    thursdayEnd = models.TimeField(verbose_name='End Time', null=True, blank=True, default='17:00')
    fridayStart = models.TimeField(verbose_name='Start Time', null=True, blank=True, default='09:00')
    fridayEnd = models.TimeField(verbose_name='End Time', null=True, blank=True, default='17:00')
    saturdayStart = models.TimeField(verbose_name='Start Time', null=True, blank=True)
    saturdayEnd = models.TimeField(verbose_name='End Time', null=True, blank=True)
    sundayStart = models.TimeField(verbose_name='Start Time', null=True, blank=True)
    sundayEnd = models.TimeField(verbose_name='End Time', null=True, blank=True)
    payFrequency = models.ForeignKey('PayFrequency', verbose_name='Pay Frequency', related_name='pay_frequency', null=True, blank=True, on_delete=models.CASCADE) 
    reservePrice = models.IntegerField(verbose_name='Reserve Price', null=True, blank=True)
    paymentTypes = models.TextField(verbose_name='Payment Types', null=True, blank=True, help_text='Comma-separated list of payment types the clinic offers.')
    paymentMethodToggle = models.BooleanField(verbose_name='Payment Method Toggle', default=False)
    paymentMethod = models.CharField(verbose_name='Payment Method', max_length=100, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    paymentMethodOther = models.CharField(verbose_name='Other Payment Method', max_length=200, null=True, blank=True)
    flatFeeType = models.CharField(verbose_name='Flat Fee Offer Type', max_length=50, null=True, blank=True, choices=FLAT_FEE_TYPE_CHOICES, help_text='Choose how flat-fee offers should be priced.')
    desiredFeeSplitPercentage = models.IntegerField(verbose_name='Desired Fee Split Percentage', null=True, blank=True)
    minimumCompensation = models.IntegerField(verbose_name='Minimum Compensation', null=True, blank=True)
    requiredSkills = models.JSONField(verbose_name='Required Skills Payload', blank=True, null=True, default=list)
    negotiablePerks = models.JSONField(verbose_name='Negotiable Perks Payload', blank=True, null=True, default=list)
    desiredFlatFeeHourly = models.DecimalField(verbose_name='Desired Flat Fee Hourly', null=True, blank=True, max_digits=10, decimal_places=2)
    desiredFlatFeeTotalContract = models.DecimalField(verbose_name='Desired Flat Fee Total Contract', null=True, blank=True, max_digits=10, decimal_places=2)
    startingBid = models.IntegerField(verbose_name='Starting Bid', null=True, blank=True, help_text='The initial bid amount.')
    minimumBidIncrement = models.IntegerField(verbose_name='Winning Offer Step', null=True, blank=True, help_text='Each new winning offer must improve by at least this amount.')
    currentLowBid = models.IntegerField(verbose_name='Current Winning Offer', blank=True, null=True)
    winner = models.ForeignKey(User, related_name='auction_winner', blank=True, null=True, on_delete=models.CASCADE)
    winningPrice = models.IntegerField(verbose_name='Winning Offer', blank=True, null=True)
    underEightteen = models.IntegerField(verbose_name='Under 18', blank=True, null=True)
    eightteenToSixtyFive = models.IntegerField(verbose_name='18 - 65', blank=True, null=True)
    overSixtyFive = models.IntegerField(verbose_name='Over 65', blank=True, null=True)
    MSK = models.IntegerField(verbose_name='MSK', blank=True, null=True)
    neuro = models.IntegerField(verbose_name='Neuro', blank=True, null=True)
    cardioResp = models.IntegerField(verbose_name='CardioResp', blank=True, null=True)
    comments = models.TextField(verbose_name='Information about the healthcare facility', blank=True, null=True)
    active = models.BooleanField(verbose_name='Active Listing')
    waitingCloseout = models.BooleanField(verbose_name='Closed Waiting Listing', default=False)
    closed = models.BooleanField(verbose_name='Closed Listing')
    deleted = models.BooleanField(verbose_name='Deleted Listing')
    cronID = models.TextField(verbose_name='Cron Job Timer ID')
    created = models.DateTimeField(verbose_name='Created Time', auto_now_add=True)
    createdBy = models.ForeignKey(User, related_name='auction_created_by', blank=True, null=True, on_delete=models.CASCADE)
    modified = models.DateTimeField(verbose_name='Modified Time', null=True, blank=True)
    modifiedBy = models.ForeignKey(User, related_name='auction_modified_by', blank=True, null=True, on_delete=models.CASCADE)
    type = models.ForeignKey(UserType, verbose_name='Listing Type', related_name='auction_type', on_delete=models.CASCADE)
    paymentType = models.ForeignKey('PaymentType', verbose_name='Payment Type ', related_name='payment_type', on_delete=models.CASCADE)
    treatmentCost = models.FloatField(verbose_name="Healthcare facility's Treatment Price", blank=True, null=True)
    treatmentMin = models.IntegerField(verbose_name='Daily Minimum # of Treatments', blank=True, null=True)
    assessmentCost = models.FloatField(verbose_name="Healthcare facility's Assessment Price", blank=True, null=True)
    assessmentMin = models.IntegerField(verbose_name='Daily Minimum # of Assessments', blank=True, null=True)
    auctionNumber = models.IntegerField(verbose_name='Listing Number', blank=True, null=True)
    
    def __str__(self):
        return str(self.clinic.clinicName) + ": " + str(self.auctionStart.strftime("%m/%d/%Y %H:%M"))

    def get_payment_types_list(self):
        payment_types = []
        if self.paymentTypes:
            payment_types = [payment_type.strip() for payment_type in self.paymentTypes.split(',') if payment_type.strip()]
        elif self.paymentType_id:
            payment_types = [self.paymentType.name]
        return payment_types

    def has_payment_type(self, payment_type_name):
        return payment_type_name in self.get_payment_types_list()

    def is_flat_fee(self):
        return self.has_payment_type('Flat Fee')

    def is_fee_split(self):
        return self.has_payment_type('Fee Split')

    def get_primary_payment_type(self):
        payment_types = self.get_payment_types_list()
        if payment_types:
            return payment_types[0]
        if self.paymentType_id:
            return self.paymentType.name
        return ''

    def get_payment_type_label(self):
        payment_type_labels = []
        if self.is_fee_split():
            payment_type_labels.append('Fee Split')
        if self.is_flat_fee():
            if self.flatFeeType == 'hourly':
                payment_type_labels.append('Flat Fee (Hourly)')
            elif self.flatFeeType == 'total_contract':
                payment_type_labels.append('Flat Fee (Total Contract Price)')
            else:
                payment_type_labels.append('Flat Fee')

        if payment_type_labels:
            return ' / '.join(payment_type_labels)

        return ''

    def get_payment_type_filter_labels(self):
        payment_type_labels = []
        if self.is_fee_split():
            payment_type_labels.append('Fee Split')
        if self.is_flat_fee():
            if self.flatFeeType == 'hourly':
                payment_type_labels.append('Flat Fee (Hourly)')
            elif self.flatFeeType == 'total_contract':
                payment_type_labels.append('Flat Fee (Total Contract Price)')

        return payment_type_labels

    def get_payment_type_badge_lines(self):
        payment_type_lines = []
        if self.is_fee_split():
            payment_type_lines.append('Fee Split')
        if self.is_flat_fee():
            payment_type_lines.append('Flat Fee')
            if self.flatFeeType == 'hourly':
                payment_type_lines.append('(Hourly)')
            elif self.flatFeeType == 'total_contract':
                payment_type_lines.append('(Total Contract Price)')

        if payment_type_lines:
            return payment_type_lines

        return ['']

    def get_bids_for_offer_type(self, offer_type):
        return Bid.objects.filter(auction=self.auctionID, active=True, offerType=offer_type).order_by('amount')

    def get_low_offer_amount(self, offer_type):
        low_bid = self.get_bids_for_offer_type(offer_type).first()
        if low_bid is not None:
            return low_bid.amount

        if offer_type == 'Flat Fee' and self.get_primary_payment_type() == 'Flat Fee':
            return self.currentLowBid
        if offer_type == 'Fee Split' and self.get_primary_payment_type() == 'Fee Split':
            return self.currentLowBid
        return None

    def get_offer_increment(self, amount):
        if amount <= 100:
            return 1
        if amount <= 10000:
            return 100
        if amount <= 25000:
            return 250
        return 500

    def get_next_available_offer_amount(self, offer_type):
        current_low = self.get_low_offer_amount(offer_type)
        if current_low is None:
            return None

        increment = self.get_offer_increment(current_low)
        diff = current_low - increment
        if diff > 0 and diff % increment == 0 and current_low > 2:
            return diff
        if diff > 0 and diff % increment != 0 and current_low > 2:
            return current_low - (diff % increment)
        if current_low == 2:
            return 1
        return 0

    def get_bid_number(self):
        if self.is_fee_split() and not self.is_flat_fee():
            return self.get_low_offer_amount('Fee Split') or 100
        if self.is_flat_fee() and not self.is_fee_split():
            return self.get_low_offer_amount('Flat Fee') or 0
        return self.currentLowBid or 0

    def get_bid(self):
        if self.closed == True and self.active == False:
            if self.winningPrice is None:
                return 'No winner'
            if self.is_fee_split() and not self.is_flat_fee():
                return 'Winning Offer: ' + str("{:,}".format(self.winningPrice)) + '%'
            return 'Winning Offer: $' + str("{:,}".format(self.winningPrice))

        flat_fee_low = self.get_low_offer_amount('Flat Fee') if self.is_flat_fee() else None
        fee_split_low = self.get_low_offer_amount('Fee Split') if self.is_fee_split() else None

        if flat_fee_low is None and fee_split_low is None:
            return '0 Offers'

        offer_labels = []
        if flat_fee_low is not None:
            offer_labels.append('$' + str("{:,}".format(flat_fee_low)))
        if fee_split_low is not None:
            offer_labels.append(str("{:,}".format(fee_split_low)) + '%')

        if len(offer_labels) == 1:
            return 'Low Offer: ' + offer_labels[0]
        return 'Low Offers: ' + ' / '.join(offer_labels)

    def get_num_bids(self):
        if self.closed and self.active == False:
            num_bids = Bid.objects.filter(auction=self.auctionID).count()
        else:
            num_bids = Bid.objects.filter(auction=self.auctionID, active=True).count()
        return num_bids

    def has_winning_offer(self):
        return self.winner_id is not None and self.winningPrice is not None

    def is_in_clinic_review_window(self):
        if not self.waitingCloseout or self.closed or self.deleted or self.auctionEnd is None:
            return False
        now = django_timezone.now()
        admin_settings = AdminSetting.objects.first()
        waiting_seconds = admin_settings.defaultClosedWaitingPeriodLength if admin_settings is not None else 604800
        review_deadline = self.auctionEnd + datetime.timedelta(seconds=waiting_seconds)
        return self.auctionEnd <= now < review_deadline

    def is_closed_waiting(self):
        return self.waitingCloseout and not self.closed and not self.deleted

    def is_effectively_closed(self):
        if self.closed and not self.active:
            return True
        if self.is_closed_waiting():
            return True
        if self.active and self.auctionEnd is not None and self.auctionEnd <= django_timezone.now():
            return True
        return False

    def is_effectively_active(self):
        return self.active and not self.is_effectively_closed()

    def get_completed_card_title(self):
        if not self.has_winning_offer():
            return 'Completed'
        return 'Winning Offer:'

    def get_listing_status_label(self):
        if self.deleted:
            return 'Deleted'
        if self.is_closed_waiting():
            return 'Closed (Waiting)'
        if self.closed or self.is_effectively_closed():
            return 'Closed'
        if self.active:
            return 'Active'
        return 'Pending'

    def get_winning_offer_display(self):
        if self.winningPrice is None:
            return 'No winner'

        winning_bid = Bid.objects.filter(
            auction=self,
            user=self.winner,
            amount=self.winningPrice,
        ).order_by('-created').first()

        if winning_bid is not None:
            if winning_bid.offerType == 'Fee Split':
                return str('{:,}'.format(self.winningPrice)) + '%'
            if winning_bid.offerType == 'Flat Fee':
                if self.flatFeeType == 'hourly':
                    return '$' + str('{:,}'.format(self.winningPrice)) + '/hr'
                return '$' + str('{:,}'.format(self.winningPrice))

        if self.is_fee_split() and not self.is_flat_fee():
            return str('{:,}'.format(self.winningPrice)) + '%'
        if self.flatFeeType == 'hourly':
            return '$' + str('{:,}'.format(self.winningPrice)) + '/hr'
        return '$' + str('{:,}'.format(self.winningPrice))

    def get_winning_offer_symbol(self):
        if self.winningPrice is None:
            return '$'

        winning_bid = Bid.objects.filter(
            auction=self,
            user=self.winner,
            amount=self.winningPrice,
        ).order_by('-created').first()

        if winning_bid is not None:
            if winning_bid.offerType == 'Fee Split':
                return '%'
            if winning_bid.offerType == 'Flat Fee':
                return '$'

        if self.is_fee_split() and not self.is_flat_fee():
            return '%'
        return '$'
    
    def get_winning_price(self):
        if self.winningPrice is not None:
            return "$" + str(self.winningPrice)
        else:
            return "None"

    def get_position_type(self):
        if str(self.clinic.userType) == 'Physiotherapy Clinic':
            return 'Temporary Physiotherapist'
        else:
            return ''

    def get_required_skill_rows(self):
        rows = []
        for item in (self.requiredSkills or []):
            if isinstance(item, dict):
                name = (item.get('name') or '').strip()
                selected = bool(item.get('selected', False))
                requirement = (item.get('requirement') or 'Required').strip() or 'Required'
                if not name:
                    continue
                if selected:
                    rows.append({'name': name, 'requirement': requirement})
        return rows

    def get_public_perk_rows(self):
        rows = []
        for item in (self.negotiablePerks or []):
            if isinstance(item, dict):
                name = (item.get('name') or '').strip()
                included = bool(item.get('selected', False) or item.get('included', False))
                if name and included:
                    rows.append({'name': name})
        return rows

    def get_private_perk_rows(self):
        rows = []
        for item in (self.negotiablePerks or []):
            if isinstance(item, dict):
                name = (item.get('name') or '').strip()
                included = bool(item.get('selected', False) or item.get('included', False))
                amount = item.get('amount')
                details = (item.get('details') or '').strip()

                try:
                    amount_value = int(amount) if amount not in (None, '') else 0
                except (TypeError, ValueError):
                    amount_value = 0

                if name and included:
                    rows.append({
                        'name': name,
                        'amount': amount_value,
                        'details': details,
                    })
        return rows

    def get_max_bid(self):
        primary_offer_type = self.get_primary_payment_type()
        next_offer_amount = self.get_next_available_offer_amount(primary_offer_type)
        if next_offer_amount is None:
            return ''
        if next_offer_amount == 1:
            if primary_offer_type == 'Fee Split':
                return 'Last Offer available: 1%'
            return 'Last Offer available: $1'
        if next_offer_amount == 0:
            if primary_offer_type == 'Fee Split':
                return 'Lowest possible offer has been reached: 1%'
            return 'Lowest possible offer has been reached: $1'
        if primary_offer_type == 'Fee Split':
            return 'Next Available Offer: ≤ ' + str("{:,}".format(next_offer_amount)) + '%'
        return 'Next Available Offer: ≤ $' + str("{:,}".format(next_offer_amount))

    def get_time_diff(self):
        distance = ((self.auctionEnd.astimezone(pytz.timezone('Canada/Eastern')) - datetime.datetime.now(pytz.timezone('utc'))).total_seconds()) * 1000
        days = math.floor(distance / (1000 * 60 * 60 * 24))
        hours = math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
        minutes = math.floor((distance % (1000 * 60 * 60)) / (1000 * 60))
        seconds = math.floor((distance % (1000 * 60)) / 1000)
        timeLeft = ''

        if days >= 0 and hours >= 0 and minutes >= 0 and seconds >= 0:
            if days > 0:
                timeLeft = timeLeft + str(days) + "d " + str(hours) + "h "
            elif days == 0 and hours > 0:
                timeLeft = timeLeft + str(hours) + "h " + str(minutes) + "m "
            elif days == 0 and hours == 0 and minutes > 0:
                timeLeft = timeLeft + str(minutes) + "m " + str(seconds) + "s"
            else:
                timeLeft = timeLeft + str(seconds) + "s"
        else:
            timeLeft = 'Completed'
  
        return timeLeft

class Bid(models.Model):
    OFFER_TYPE_CHOICES = (
        ('Flat Fee', 'Flat Fee'),
        ('Fee Split', 'Fee Split'),
    )

    bidID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auction = models.ForeignKey(Auction, related_name='auction', on_delete=models.CASCADE) 
    user = models.ForeignKey(User, related_name='user', blank=True, null=True, on_delete=models.CASCADE) 
    amount = models.IntegerField(verbose_name='Amount1', blank=True, null=True, help_text='Enter the amount you would like to bid.')
    offerType = models.CharField(verbose_name='Offer Type', max_length=20, choices=OFFER_TYPE_CHOICES, blank=True, null=True)
    submissionGroup = models.UUIDField(verbose_name='Submission Group', blank=True, null=True)
    selectedSkills = models.JSONField(verbose_name='Selected Skills', blank=True, null=True, default=list)
    active = models.BooleanField(verbose_name='Active Bid')
    created = models.DateTimeField(verbose_name='Created Time', auto_now_add=True)
    createdBy = models.ForeignKey(User, related_name='bid_created_by', blank=True, null=True, on_delete=models.CASCADE)
    modified = models.DateTimeField(verbose_name='Modified Time', null=True, blank=True)
    modifiedBy = models.ForeignKey(User, related_name='bid_modified_by', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user) #+ ': $' + str(self.amount)

class Demographic(models.Model):
    auction = models.ForeignKey(Auction, related_name='demogrpahic_auction', on_delete=models.CASCADE, default=1)
    category = models.ForeignKey('DemographicType', related_name='category', on_delete=models.CASCADE)
    percentage = models.IntegerField(verbose_name='Percentage')  

    def __str__(self):
        return str(self.auction.clinic) + " - " + str(self.category) + ": " + str(self.percentage) + "%"

    def get_category(self):
        return str(self.category)

    def get_percentage(self):
        return str(self.percentage)

class DemographicType(models.Model):
    name = models.CharField(verbose_name='Demographic', max_length=200, help_text='Select a demographic type.')

    def __str__(self):
        return str(self.name)

class PayFrequency(models.Model):
    name = models.CharField(verbose_name='Pay Frequency', max_length=200, help_text='Select a pay frequency.')

    def __str__(self):
        return str(self.name)

class PracticeArea(models.Model):
    auction = models.ForeignKey(Auction, related_name='practice_area_auction', on_delete=models.CASCADE, default=1, null=True, blank=True,)
    category = models.ForeignKey('PracticeAreaType', related_name='practice_area_type', on_delete=models.CASCADE, null=True, blank=True,)
    percentage = models.IntegerField(verbose_name='Percentage', null=True, blank=True,) 

    def __str__(self):
        return str(self.auction.clinic) + " - " + str(self.category) + ": " + str(self.percentage) + "%"

    def get_category(self):
        return str(self.category)

    def get_percentage(self):
        return str(self.percetnage)

class PracticeAreaType(models.Model):
    name = models.CharField(verbose_name='Practice Area', max_length=200, help_text='Select a practice area.')
    userType = models.ForeignKey(UserType, related_name='practice_area_user_type', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.name)

class ProMember(models.Model):
    clinic = models.ForeignKey(Account, related_name='pro_member_clinic', on_delete=models.CASCADE)  
    proStart = models.DateTimeField(verbose_name='Start of Pro Membership')
    proEnd = models.DateTimeField(verbose_name='End of Pro Membership', null=True, blank=True)

    def __str__(self):
        return str(self.clinic)

class AdminSetting(models.Model):
    sendEmails = models.BooleanField(verbose_name='Send Emails', help_text='Turns on and off emails. If checked emails will send.')
    numAllowedAuctions = models.IntegerField(verbose_name='# Allowed Listing', help_text='Global setting for max number of active listing')
    defaultAuctionLength = models.IntegerField(verbose_name='Default Listing Length in Seconds', help_text='Listing will be set to this length, in seconds.')
    defaultClosedWaitingPeriodLength = models.IntegerField(verbose_name='Default Closed Waiting Period in Seconds', help_text='Closed (Waiting) listings will remain in that state for this many seconds before fully closing.', default=604800)
    endAuctionEmailBatchSize = models.IntegerField(verbose_name='End of Listing Email Batch Size', help_text='At the end of an listing emails will be sent to user with the same type as the listing. To avoid spamming email batches are limited to this number.')

    def __str__(self):
        return 'Admin Settings'

class Page(models.Model):
    page = models.CharField(verbose_name='Page', max_length=200, help_text='Name of the page.')

    def __str__(self):
       return str(self.page)

class PopupMessage(models.Model):
    page = models.ForeignKey(Page, related_name='page_popup_message', on_delete=models.CASCADE)
    message = models.CharField(verbose_name='Popup Message', max_length=5000, help_text='Message to be displayed in the popup.')
    active = models.BooleanField(verbose_name='Active', help_text='Is the popup currently active.')
    title = models.CharField(verbose_name='Popup Box Title', max_length=5000, help_text='The title of the popup box.')
    show_unauthenticated_users = models.BooleanField(verbose_name='Show to Non-logged in users', help_text='Should the pop-up be shown to non-users.')
    clickID = models.CharField(verbose_name='Clickable Item ID', max_length=5000, help_text='The ID for the item being clicked to trigger the pop-up. For non-clickable messages leave blank.', blank=True, null=True)

    def __str__(self):
        return str(self.page) + ' | ' + str(self.message)

class MessageAcknowledgement(models.Model):
    user = models.ForeignKey(User, related_name='user_message_acknowledgement', on_delete=models.CASCADE)
    popup = models.ForeignKey(PopupMessage, related_name='user_message_acknowledgement', on_delete=models.CASCADE)
    acknowledged = models.BooleanField(verbose_name='Acknowledged', help_text='Has the popup been acknowledged.')

    def __str__(self):
        return str(self.user) + ' | ' + str(self.popup)
    
class Number(models.Model):
    category = models.CharField(verbose_name='Cateogry', max_length=200, help_text='Cateogry for the number.')
    currentValue = models.IntegerField(verbose_name='Current Counter Value', help_text="The counter's current value.")

    def __str__(self):
        return str(self.category)

class Raffle(models.Model):
    AUDIENCE_CHOICES = [
        ('Both', 'Both'),
        ('Clinician', 'Clinician'),
        ('Clinic', 'Clinic'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    tickets_required = models.IntegerField(default=1)
    image_icon = models.CharField(max_length=50, default='confirmation_number', help_text='Material icon name')
    value_text = models.CharField(max_length=100, blank=True, null=True, help_text='e.g., $50 Value')
    target_audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='Both', help_text='Who can see and enter this raffle?')
    image = models.ImageField(upload_to='raffle_images/', null=True, blank=True, help_text='Upload an image less than 5MB. If not provided, the Material Icon will be used.')
    active = models.BooleanField(default=True)
    startDate = models.DateTimeField(null=True, blank=True)
    endDate = models.DateTimeField(null=True, blank=True)
    winner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='won_raffles')
    numWinningTickets = models.IntegerField(null=True, blank=True)
    cronID = models.TextField(verbose_name='Cron Job Timer ID', blank=True, null=True)

    def __str__(self):
        return self.title

class RaffleEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='raffle_entries')
    raffle = models.ForeignKey(Raffle, on_delete=models.CASCADE, related_name='entries')
    tickets_added = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def entries_count(self):
        if self.raffle.tickets_required > 0:
            return self.tickets_added // self.raffle.tickets_required
        return self.tickets_added

    def __str__(self):
        return f"{self.user.username} - {self.raffle.title}"