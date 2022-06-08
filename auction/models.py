import os
from tabnanny import verbose
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import uuid

from django.dispatch import receiver

PROVINCES = (
    ("", "---------"),
    ("Alberta", "Alberta"),
    ("British Columbia", "British Columbia"),
    ("Manitoba", "Manitoba"),
    ("New Brunswick", "New Brunswick"),
    ("Newfoundland and Labrador", "Newfoundland and Labrador"),
    ("Nova Scotia", "Nova Scotia"),
    ("Ontario", "Ontario"),
    ("Prince Edward Island", "Prince Edward Island"),
    ("Quebec", "Quebec"),
    ("Saskatchewan", "Saskatchewan")
)

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    clinicName = models.CharField(verbose_name='Clinic Name', max_length=200, blank=True, null=True, help_text='Enter the clinic name.')
    userType = models.ForeignKey('UserType', verbose_name='User Type', blank=True, null=True, related_name='usertypes', on_delete=models.CASCADE)  
    licenseNumber = models.CharField(verbose_name='License Number', max_length=120, null=True, blank=True, help_text='Enter you license number.')
    imageOne = models.ImageField(default='default.jpg', verbose_name='Clinic Image One', upload_to='images', blank=True, null=True, help_text='Upload an image (optional).')
    imageTwo = models.ImageField(verbose_name='Clinic Image Two', upload_to='images/', blank=True, null=True, help_text='Upload an image (optional).')
    imageThree = models.ImageField(verbose_name='Clinic Image Three', upload_to='images/', blank=True, null=True, help_text='Upload an image (optional).')
    imageFour = models.ImageField(verbose_name='Clinic Image Four', upload_to='images/', blank=True, null=True, help_text='Upload an image (optional).')
    city = models.CharField(verbose_name='City', max_length=120, blank=True, null=True, help_text='Enter the city your clinic is in.')
    country = models.CharField(verbose_name='Conutry', max_length=100, blank=True, null=True, help_text='Enter the country your clinic is in.')
    province = models.CharField(verbose_name='Province', help_text='The province the clinic resides in.', blank=True, null=True, max_length=30, choices=PROVINCES)
    about = models.TextField(verbose_name='About the clinic', blank=True, null=True, help_text='Tell us about your clinic.')
    practiceArea = models.ManyToManyField('PracticeArea', blank=True)
    demographic = models.ManyToManyField('Demographic', blank=True)
    pro = models.BooleanField(verbose_name='Pro Member', null=True, blank=True)

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

class Auction(models.Model):
    auctionID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Account, related_name='auction_clinic', on_delete=models.CASCADE)  
    auctionStart = models.DateTimeField(verbose_name='Auction Start', help_text='Enter the start date of the auction.')
    auctionEnd = models.DateTimeField(verbose_name='Auction End', help_text='Enter the end date of the auction.')
    placementStart = models.DateField(verbose_name='Therapist Start Date', help_text='Enter the start date of the placement.')
    placementEnd = models.DateField(verbose_name='Therapist End Date', help_text='Enter the end date of the placement.')
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
    payFrequency = models.ForeignKey('PayFrequency', verbose_name='Pay Frequency', related_name='pay_frequency', on_delete=models.CASCADE) 
    reservePrice = models.IntegerField(verbose_name='Reserve Price', null=True, blank=True, help_text='Reserve bid is the maximum price the clinic is willing to offer.')
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
    created = models.DateTimeField(verbose_name='Created Time', auto_now_add=True)
    createdBy = models.ForeignKey(User, related_name='auction_created_by', blank=True, null=True, on_delete=models.CASCADE)
    modified = models.DateTimeField(verbose_name='Modified Time', null=True, blank=True)
    modifiedBy = models.ForeignKey(User, related_name='auction_modified_by', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.clinic.clinicName) + ": " + str(self.auctionStart.strftime("%m/%d/%Y"))

    def get_bid(self):
        if self.currentLowBid is None:
            return str('No Bids Yet')
        elif self.closed == True and self.active == False:
            return 'Winning bid: $' + str(self.winningPrice)
        else:
            return 'Current Low Bid: $' + str(self.currentLowBid)

    def get_num_bids(self):
        num_bids = Bid.objects.filter(auction=self.auctionID).count()
        return num_bids

class Bid(models.Model):
    bidID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auction = models.ForeignKey(Auction, related_name='auction', on_delete=models.CASCADE) 
    user = models.ForeignKey(User, related_name='user', blank=True, null=True, on_delete=models.CASCADE) 
    amount = models.IntegerField(verbose_name='Amount', help_text='Enter the amount you would like to bid.')
    active = models.BooleanField(verbose_name='Active Bid')
    created = models.DateTimeField(verbose_name='Created Time', auto_now_add=True)
    createdBy = models.ForeignKey(User, related_name='bid_created_by', blank=True, null=True, on_delete=models.CASCADE)
    modified = models.DateTimeField(verbose_name='Modified Time', null=True, blank=True)
    modifiedBy = models.ForeignKey(User, related_name='bid_modified_by', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        # return str(self.user)
        return "123"

class Demographic(models.Model):
    clinic = models.ForeignKey(Account, related_name='demogrpahic_clinic', on_delete=models.CASCADE)
    category = models.ForeignKey('DemographicType', related_name='category', on_delete=models.CASCADE)
    percentage = models.IntegerField(verbose_name='Percentage', help_text='Enter the percentage your clinic works with the given demographic.')  

    def __str__(self):
        return str(self.clinic.clinicName) + " - " + str(self.category) + ": " + str(self.percentage) + "%"

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
    clinic = models.ForeignKey(Account, related_name='practice_area_clinic', on_delete=models.CASCADE)
    category = models.ForeignKey('PracticeAreaType', related_name='practice_area_type', on_delete=models.CASCADE)
    percetnage = models.IntegerField(verbose_name='Percentage', help_text='Enter the percentage your clinic works with the given demographic.')  

    def __str__(self):
        return str(self.clinic.clinicName) + " - " + str(self.category) + ": " + str(self.percetnage) + "%"

    def get_category(self):
        return str(self.category)

    def get_percentage(self):
        return str(self.percetnage)

class PracticeAreaType(models.Model):
    name = models.CharField(verbose_name='Practice Area', max_length=200, help_text='Select a practice area.')

    def __str__(self):
        return str(self.name)

class ProMember(models.Model):
    clinic = models.ForeignKey(Account, related_name='pro_member_clinic', on_delete=models.CASCADE)  
    proStart = models.DateTimeField(verbose_name='Start of Pro Membership')
    proEnd = models.DateTimeField(verbose_name='End of Pro Membership', null=True, blank=True)

    def __str__(self):
        return str(self.clinic)

class UserType(models.Model):
    name = models.CharField(verbose_name='User Type', max_length=200, help_text='Select a user type')

    def __str__(self):
        return self.name

class AdminSettings(models.Model):
    sendEmails = models.BooleanField(verbose_name='Send Emails', help_text='Turns on and off emails. If checked emails will send.')
    numAllowedAuctions = models.IntegerField(verbose_name='# Allowed Auctions', help_text='Global setting for max number of active auctions')

    def __str__(self):
        return 'Admin Settings'



