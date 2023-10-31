from pytz import timezone
import datetime
import math
import os
from tabnanny import verbose
from unicodedata import category
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
    feeSplit = models.BooleanField(verbose_name='Allowed Fee Split', help_text='If checked this user type will be allowed to select fee split as a payment type.')

    def __str__(self):
        return self.name

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    clinicName = models.CharField(verbose_name='Clinic Name', max_length=200, blank=True, null=True, help_text='Enter the clinic name.')
    userType = models.ForeignKey(UserType, verbose_name='User Type', blank=True, null=True, related_name='usertypes', on_delete=models.CASCADE)  
    licenseNumber = models.CharField(verbose_name='License Number', max_length=120, null=True, blank=True, help_text='Enter you license number.')
    imageOne = models.ImageField(default='default.jpg', verbose_name='Clinic Image One', upload_to=path_and_rename, blank=True, null=True, help_text='Upload an image (optional).')
    imageTwo = models.ImageField(verbose_name='Clinic Image Two', upload_to=path_and_rename, blank=True, null=True, help_text='Upload an image (optional).')
    imageThree = models.ImageField(verbose_name='Clinic Image Three', upload_to=path_and_rename, blank=True, null=True, help_text='Upload an image (optional).')
    imageFour = models.ImageField(verbose_name='Clinic Image Four', upload_to=path_and_rename, blank=True, null=True, help_text='Upload an image (optional).')
    city = models.CharField(verbose_name='City', max_length=120, blank=True, null=True, help_text='Enter the city your clinic is in.')
    country = models.CharField(verbose_name='Conutry', max_length=100, blank=True, null=True, help_text='Enter the country your clinic is in.')
    province = models.CharField(verbose_name='Province', help_text='The province the clinic resides in.', blank=True, null=True, max_length=30, choices=PROVINCES)
    about = models.TextField(verbose_name='About the clinic', blank=True, null=True, help_text='Tell us about your clinic.')
    underEighteen = models.IntegerField(verbose_name='% Under 18', blank=True, null=True)
    eighteenToSixtyFive = models.IntegerField(verbose_name='% 18 - 65', blank=True, null=True)
    overSixtyFive = models.IntegerField(verbose_name='% Over 65', blank=True, null=True)
    MSK = models.IntegerField(verbose_name='% Musculoskeletal', blank=True, null=True)
    neuro = models.IntegerField(verbose_name='% Neurological', blank=True, null=True)
    cardioResp = models.IntegerField(verbose_name='% Cardiorespiratory', blank=True, null=True)
    practiceArea = models.ManyToManyField('PracticeArea', blank=True)
    demographic = models.ManyToManyField('Demographic', blank=True)
    pro = models.BooleanField(verbose_name='Pro Member', null=True, blank=True)
    remember_auction_data = models.BooleanField(verbose_name='Do you want your data to be pre-populated for your next auction?', null=True, blank=True)
    auction_message_displayed = models.BooleanField(verbose_name='Auction Message Displayed', null=True, blank=True)

    def __str__(self):
        return str(self.user)

    @receiver(post_save, sender=User)
    def update_profile_signal(sender, instance, created, **kwargs):
        print("inside update profile")
        if created:
            Account.objects.create(user=instance)
        instance.account.save()

    def get_split_user_type(self):
        return str(self.userType).split(' ')[-1]

class PaymentType(models.Model):
    name = models.CharField(verbose_name='Payment Type', max_length=200, help_text='Select a payment type from the list.')

    def __str__(self):
        return str(self.name)

class Auction(models.Model):
    auctionID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Account, related_name='auction_clinic', on_delete=models.CASCADE)
    auctionStart = models.DateTimeField(verbose_name='Auction Start', help_text='Enter the start date of the auction.')
    auctionEnd = models.DateTimeField(verbose_name='Auction End', help_text='Enter the end date of the auction.')
    placementStart = models.DateField(verbose_name='Therapist Start Date', help_text='Enter the start date of the placement.', default=datetime.date.today)
    placementEnd = models.DateField(verbose_name='Therapist End Date', help_text='Enter the end date of the placement.', default=datetime.date.today)
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
    startingBid = models.IntegerField(verbose_name='Starting Bid', null=True, blank=True, help_text='The intial bid amount.')
    minimumBidIncrement = models.IntegerField(verbose_name='Minimum Bid Increment', null=True, blank=True, help_text='All bids must decrease by the minimum bid increment.')
    currentLowBid = models.IntegerField(verbose_name='Current Low Bid', blank=True, null=True)
    winner = models.ForeignKey(User, related_name='auction_winner', blank=True, null=True, on_delete=models.CASCADE)
    winningPrice = models.IntegerField(verbose_name='Winning Price', blank=True, null=True)
    underEightteen = models.IntegerField(verbose_name='Under 18', blank=True, null=True)
    eightteenToSixtyFive = models.IntegerField(verbose_name='18 - 65', blank=True, null=True)
    overSixtyFive = models.IntegerField(verbose_name='Over 65', blank=True, null=True)
    MSK = models.IntegerField(verbose_name='MSK', blank=True, null=True)
    neuro = models.IntegerField(verbose_name='Neuro', blank=True, null=True)
    cardioResp = models.IntegerField(verbose_name='CardioResp', blank=True, null=True)
    comments = models.TextField(verbose_name='Information about the Clinic', blank=True, null=True)
    active = models.BooleanField(verbose_name='Active Auction')
    closed = models.BooleanField(verbose_name='Closed Auction')
    deleted = models.BooleanField(verbose_name='Deleted Auction')
    cronID = models.TextField(verbose_name='Cron Job Timer ID')
    created = models.DateTimeField(verbose_name='Created Time', auto_now_add=True)
    createdBy = models.ForeignKey(User, related_name='auction_created_by', blank=True, null=True, on_delete=models.CASCADE)
    modified = models.DateTimeField(verbose_name='Modified Time', null=True, blank=True)
    modifiedBy = models.ForeignKey(User, related_name='auction_modified_by', blank=True, null=True, on_delete=models.CASCADE)
    type = models.ForeignKey(UserType, verbose_name='Auction Type', related_name='auction_type', on_delete=models.CASCADE)
    paymentType = models.ForeignKey('PaymentType', verbose_name='Payment Type ', related_name='payment_type', on_delete=models.CASCADE)
    treatmentCost = models.FloatField(verbose_name="Clinic's Treatment Price", blank=True, null=True)
    treatmentMin = models.IntegerField(verbose_name='Daily Minimum # of Treatments', blank=True, null=True)
    assessmentCost = models.FloatField(verbose_name="Clinic's Assessment Price", blank=True, null=True)
    assessmentMin = models.IntegerField(verbose_name='Daily Minimum # of Assessments', blank=True, null=True)
    auctionNumber = models.IntegerField(verbose_name='Auction Number', blank=True, null=True)

    def __str__(self):
        return str(self.clinic.clinicName) + ": " + str(self.auctionStart.strftime("%m/%d/%Y %H:%M"))

    def get_bid(self):
        print(self.paymentType)
        if self.currentLowBid is None:
            return str('0 bids')
        elif self.reservePrice is not None and (self.closed == True and self.active == False and self.winningPrice > self.reservePrice):
            return 'Reserve price not met'
        elif self.closed == True and self.active == False and self.winningPrice is not None:
            if str(self.paymentType) == 'Flat Fee':
                return 'Winning bid: $' + str("{:,}".format(self.winningPrice))
            elif str(self.paymentType) == 'Fee Split':
                return 'Winning bid: ' + str("{:,}".format(self.winningPrice)) + '%'
        elif self.closed == True and self.active == False and self.winningPrice is None:
            return 'No winner'
        else:
            if str(self.paymentType) == 'Flat Fee':
                return 'Low Bid: $' + str("{:,}".format(self.currentLowBid))
            elif str(self.paymentType) == 'Fee Split':
                return 'Low Bid: ' + str("{:,}".format(self.currentLowBid)) + '%'
            
    def get_bid_number(self):
        if self.currentLowBid is None:
            return 0
        elif self.reservePrice is not None and (self.closed == True and self.active == False and self.winningPrice > self.reservePrice):
            return 0
        elif self.closed == True and self.active == False and self.winningPrice is not None:
            if str(self.paymentType) == 'Flat Fee':
                return self.winningPrice
            elif str(self.paymentType) == 'Fee Split':
                return self.winningPrice
        elif self.closed == True and self.active == False and self.winningPrice is None:
            return 0
        else:
            if str(self.paymentType) == 'Flat Fee':
                return self.currentLowBid
            elif str(self.paymentType) == 'Fee Split':
                return self.currentLowBid

    def get_num_bids(self):
        num_bids = Bid.objects.filter(auction=self.auctionID, active=True).count()
        return num_bids

    def get_position_type(self):
        if str(self.clinic.userType) == 'Physiotherapy Clinic':
            return 'Temporary Physiotherapist'
        else:
            return ''

    def get_max_bid(self):
        num_bids = Bid.objects.filter(auction=self.auctionID).count()
        if num_bids > 0 and self.currentLowBid is not None and self.minimumBidIncrement is not None:
            diff = self.currentLowBid - self.minimumBidIncrement
            if diff > 0 and diff % self.minimumBidIncrement == 0 and self.currentLowBid > 2:
                if str(self.paymentType) == 'Flat Fee':
                    return 'Next Available Bid: ≤ $' + str("{:,}".format(diff))
                elif str(self.paymentType) == 'Fee Split':
                    return 'Next Available Bid: ≤ ' + str("{:,}".format(diff)) + "%"
            elif diff > 0 and diff % self.minimumBidIncrement != 0 and self.currentLowBid > 2:
                result = self.currentLowBid - (diff % self.minimumBidIncrement)
                if str(self.paymentType) == 'Flat Fee':
                    return 'Next Available Bid: ≤ $' + str("{:,}".format(result))
                elif str(self.paymentType) == 'Fee Split':
                    return 'Next Available Bid: ≤ ' + str("{:,}".format(result)) + "%"
            elif self.currentLowBid == 2:
                if str(self.paymentType) == 'Flat Fee':
                    return 'Last bid available: $1'
                elif str(self.paymentType) == 'Fee Split':
                    return 'Last bid available: 1%'
            else:
                if str(self.paymentType) == 'Flat Fee':
                    return 'Lowest possible bid has been reached: $1'
                elif str(self.paymentType) == 'Fee Split':
                    return 'Lowest possible bid has been reached: 1%'
        else:
            return 0

    def get_time_diff(self):
        distance = ((self.auctionEnd.astimezone(timezone('Canada/Eastern')) - datetime.datetime.now(timezone('utc'))).total_seconds()) * 1000
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
            timeLeft = 'Auction Completed'
        
        return timeLeft

class Bid(models.Model):
    bidID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auction = models.ForeignKey(Auction, related_name='auction', on_delete=models.CASCADE) 
    user = models.ForeignKey(User, related_name='user', blank=True, null=True, on_delete=models.CASCADE) 
    amount = models.IntegerField(verbose_name='Amount1', blank=True, null=True, help_text='Enter the amount you would like to bid.')
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

class AdminSettings(models.Model):
    sendEmails = models.BooleanField(verbose_name='Send Emails', help_text='Turns on and off emails. If checked emails will send.')
    numAllowedAuctions = models.IntegerField(verbose_name='# Allowed Auctions', help_text='Global setting for max number of active auctions')
    defaultAuctionLength = models.IntegerField(verbose_name='Default Auction Length in Seconds', help_text='Auctions will be set to this length, in seconds.')

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