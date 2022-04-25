from tabnanny import verbose
from unicodedata import category
from django.db import models
from django.contrib.auth.models import User
# from localflavor.ca.models import CAProvinceField
import uuid

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    clinicName = models.CharField(verbose_name='Clinic Name', max_length=200, blank=True, null=True, help_text='Enter the clinic name.')
    userType = models.ForeignKey('UserType', related_name='usertypes', on_delete=models.CASCADE)  
    licenseNumber = models.CharField(verbose_name='License Number', max_length=120, null=True, blank=True, help_text='Enter you license number.')
    imageOne = models.ImageField(verbose_name='Clinic Image One', upload_to='images/', blank=True, null=True, help_text='Upload an image (optional).')
    imageTwo = models.ImageField(verbose_name='Clinic Image Two', upload_to='images/', blank=True, null=True, help_text='Upload an image (optional).')
    imageThree = models.ImageField(verbose_name='Clinic Image Three', upload_to='images/', blank=True, null=True, help_text='Upload an image (optional).')
    imageFour = models.ImageField(verbose_name='Clinic Image Four', upload_to='images/', blank=True, null=True, help_text='Upload an image (optional).')
    city = models.CharField(verbose_name='City', blank=True, max_length=120, null=True, help_text='Enter the city your clinic is in.')
    # province = models.CAProvinceField('Province')
    country = models.CharField(verbose_name='Conutry', max_length=100, help_text='Enter the country your clinic is in.')
    about = models.TextField(verbose_name='About', blank=True, null=True, help_text='Tell us about your clinic.')
    practiceArea = models.ManyToManyField('PracticeArea', blank=True)
    demographic = models.ManyToManyField('Demographic', blank=True)

    def __str__(self):
        return str(self.user)

class Auction(models.Model):
    auctionID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clinic = models.ForeignKey(Account, related_name='auction_clinic', on_delete=models.CASCADE)  
    auctionStart = models.DateTimeField(verbose_name='Auction Start', null=True, blank=True, help_text='Enter the start date of the auction.')
    auctionEnd = models.DateTimeField(verbose_name='Auction End', null=True, blank=True, help_text='Enter the end date of the auction.')
    placementStart = models.DateField(verbose_name='Auction End', null=True, blank=True, help_text='Enter the start date of the placement.')
    placementEnd = models.DateField(verbose_name='Auction End', null=True, blank=True, help_text='Enter the end date of the placement.')
    mondayStart = models.TimeField(verbose_name='Monday Start Time', null=True, blank=True, help_text='Enter the start of the workday on Mondays.')
    mondayEnd = models.TimeField(verbose_name='Monday End Time', null=True, blank=True, help_text='Enter the end of the workday on Mondays.')
    tuesdayStart = models.TimeField(verbose_name='Tuesday Start Time', null=True, blank=True, help_text='Enter the start of the workday on Tuesdays.')
    tuesdayEnd = models.TimeField(verbose_name='Tuesday End Time', null=True, blank=True, help_text='Enter the end of the workday on Tuesdays.')
    wednesdayStart = models.TimeField(verbose_name='Wednesday Start Time', null=True, blank=True, help_text='Enter the start of the workday on Wednesdays.')
    wednesdayEnd = models.TimeField(verbose_name='Wednesday End Time', null=True, blank=True, help_text='Enter the end of the workday on Wednesdays.')
    thursdayStart = models.TimeField(verbose_name='Thursday Start Time', null=True, blank=True, help_text='Enter the start of the workday on Thursdays.')
    thursdayEnd = models.TimeField(verbose_name='Thursday End Time', null=True, blank=True, help_text='Enter the end of the workday on Thursdays.')
    fridayStart = models.TimeField(verbose_name='Friday Start Time', null=True, blank=True, help_text='Enter the start of the workday on Fridays.')
    fridayEnd = models.TimeField(verbose_name='Friday End Time', null=True, blank=True, help_text='Enter the end of the workday on Fridays.')
    saturdayStart = models.TimeField(verbose_name='Saturday Start Time', null=True, blank=True, help_text='Enter the start of the workday on Saturdays.')
    saturdayEnd = models.TimeField(verbose_name='Saturday End Time', null=True, blank=True, help_text='Enter the end of the workday on Saturdays.')
    sundayStart = models.TimeField(verbose_name='Sunday Start Time', null=True, blank=True, help_text='Enter the start of the workday on Sundays.')
    sundayEnd = models.TimeField(verbose_name='Sunday End Time', null=True, blank=True, help_text='Enter the end of the workday on Sundays.')
    payFrequency = models.ForeignKey('PayFrequency', related_name='pay_frequency', on_delete=models.CASCADE) 
    reservePrice = models.IntegerField(verbose_name='Reserve Price', help_text='Reserve bid is the maximum price the clinic is willing to offer.')
    minimumBidIncrement = models.IntegerField(verbose_name='Minimum Bid Increment', help_text='All bids must decrease by the minimum bid increment.')
    currentLowBid = models.IntegerField(verbose_name='Current Low Bid', blank=True, null=True)
    winner = models.ForeignKey(User, related_name='auction_winner', blank=True, null=True, on_delete=models.CASCADE)
    winningPrice = models.IntegerField(verbose_name='Winning Price', blank=True, null=True)
    active = models.BooleanField(verbose_name='Active Auction')
    closed = models.BooleanField(verbose_name='Closed Auction')
    deleted = models.BooleanField(verbose_name='Deleted Auction')
    created = models.DateTimeField(verbose_name='Created Time')
    createdBy = models.ForeignKey(User, related_name='auction_created_by', blank=True, null=True, on_delete=models.CASCADE)
    modified = models.DateTimeField(verbose_name='Modified Time', null=True, blank=True)
    modifiedBy = models.ForeignKey(User, related_name='auction_modified_by', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.clinic) + ": " + str(self.auctionStart.strftime("%m/%d/%Y"))

class Bid(models.Model):
    bidID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    auction = models.ForeignKey(Auction, related_name='auction', on_delete=models.CASCADE) 
    user = models.ForeignKey(User, related_name='user', blank=True, null=True, on_delete=models.CASCADE) 
    amount = models.IntegerField(verbose_name='Amount', help_text='Enter the amount you would like to bid.')
    active = models.BooleanField(verbose_name='Active Bid')
    created = models.DateTimeField(verbose_name='Created Time')
    createdBy = models.ForeignKey(User, related_name='bid_created_by', blank=True, null=True, on_delete=models.CASCADE)
    modified = models.DateTimeField(verbose_name='Modified Time', null=True, blank=True)
    modifiedBy = models.ForeignKey(User, related_name='bid_modified_by', blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        # return str(self.user)
        return "123"

class Demographic(models.Model):
    clinic = models.ForeignKey(Account, related_name='demogrpahic_clinic', on_delete=models.CASCADE)
    category = models.ForeignKey('DemographicType', related_name='category', on_delete=models.CASCADE)
    percetnage = models.IntegerField(verbose_name='Percentage', help_text='Enter the percentage your clinic works with the given demographic.')  

    def __str__(self):
        return str(self.clinic.name) + " - " + str(self.category) + ": " + str(self.percetnage) + "%"

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
        return str(self.clinic.name) + " - " + str(self.category) + ": " + str(self.percetnage) + "%"

class PracticeAreaType(models.Model):
    name = models.CharField(verbose_name='Practice Area', max_length=200, help_text='Select a practice area.')

    def __str__(self):
        return str(self.name)

class UserType(models.Model):
    name = models.CharField(verbose_name='User Type', max_length=200, help_text='Select a user type')

    def __str__(self):
        return self.name



