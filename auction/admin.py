from tabnanny import verbose
from unicodedata import category
from django import forms
from django.contrib import admin
from django.http import BadHeaderError, HttpResponse
from .models import Auction, Bid, Account, PayFrequency, PracticeArea, PracticeAreaType, ProMember, UserType, Demographic, DemographicType, ProMember, AdminSetting, Page, PopupMessage, MessageAcknowledgement, PaymentType, Number
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.conf import settings
from . import emails
from The_Travelling_Therapist.settings import ENVIRONMENT, DEV_LINK, PROD_LINK
from datetime import datetime, timedelta
import time

class BidInline(admin.TabularInline):
    model = Bid
    ordering = ('amount',)

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    readonly_fields = ('cronID',)
    list_display = ('auctionID', 'auctionNumber', 'clinic', 'paymentType', 'auctionStart', 'auctionEnd', 'active', 'closed', 'placementStart', 'placementEnd', 'winner', 'winningPrice')
    # Reverse alpahbetical order -name
    ordering = ('-auctionNumber', )
    search_fields = ('auctionID',)
    inlines = [BidInline]
    exclude = ['startingBid', 'underEightteen', 'eightteenToSixtyFive', 'overSixtyFive', 'MSK', 'neuro', 'cardioResp', 'payFrequency']

    def save_model(self, request, obj, form, change):
        admin = AdminSetting.objects.first()
        auction = Auction.objects.get(pk=obj.auctionID)
        print("auction = " + str(auction.active))
        print("obj = " + str(obj.active))

        # Query the user list for users that are the same type as the auction
        print(auction.type)
        accounts = Account.objects.filter(userType=auction.type)
        print(accounts)

        if obj.active and admin.sendEmails and not auction.active:
            try:
                send_mail(
                    subject = str(obj.clinic.clinicName) + " Your Auction is Live!",
                    message = "",
                    html_message = emails.clinic_auction_live(str(obj.clinic.clinicName)),
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list = (obj.clinic.user.email,)
                )
            except BadHeaderError:
                    return HttpResponse('Invalid header found.')
            
            try:
                send_mail(
                    subject = str(obj.clinic.clinicName) + " Your Auction is Live!",
                    message = "",
                    html_message = "**ADMIN COPY**" + emails.clinic_auction_live(str(obj.clinic.clinicName)),
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list = ('info@travelingtherapist.ca',)
                )
            except BadHeaderError:
                    return HttpResponse('Invalid header found.')
            
            # Email users of the auction type that there is a new auction available for bidding
            link  = ""
            if ENVIRONMENT == "DEV":
                link = DEV_LINK + "/auction/" + str(auction.auctionID)
            else:
                link = PROD_LINK + "/auction/" + str(auction.auctionID)

            email_count = 0
            admin_setting = AdminSetting.objects.first()
            batch_size = admin_setting.endAuctionEmailBatchSize

            for account in accounts:
                print(str(auction.paymentType))
                if email_count < batch_size:
                    try:
                        send_mail(
                            subject = "NEW AUCTION - The Traveling Therapist",
                            message = "",
                            html_message = emails.new_auction_email_to_all(account.user.first_name, account.user.last_name, link, str(auction.placementStart), str(auction.placementEnd), str(auction.paymentType), auction.clinic.clinicName, auction.clinic.city + ", " + auction.clinic.province, time_diff_from_now(auction.auctionEnd)),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = (account.user.email, "loribine@gmail.com")
                        )
                    except BadHeaderError:
                            return HttpResponse('Invalid header found.')
                    email_count += 1
                    # time.sleep(5)
                else:
                    missing_email_string = ""
                    for account in accounts[email_count:]:
                        print(account)
                        missing_email_string += str(account) + "<br>"
                    try:
                        send_mail(
                            subject = "**ADMIM COPY** New Auction Batch Total Surpassed",
                            message = "",
                            html_message = "The total number of emails that can be sent has been surpassed. The total number of emails to send was " + str(len(accounts)) + " and the max that can be sent is " + str(batch_size) + ". <br><br> The following people did not get emails: <br>" + missing_email_string,
                            from_email = settings.EMAIL_HOST_USER,
                            # recipient_list = ('loribine@gmail.com',)
                            recipient_list = ('info@travelingtherapist.ca',)
                        )
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    break            
        super().save_model(request, obj, form, change)

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('bidID', 'auction', 'user', 'amount')
    ordering = ('bidID', )
    search_fields = ('bidID', 'auction')

    # Delete bids from the overview page
    def delete_queryset(self, request, queryset):
        delete_bid(queryset)

    # Delete bids from the bid detail page
    def delete_model(self, request, obj):
        print('==========================delete_model==========================')
        print(obj)

        """
        you can do anything here BEFORE deleting the object
        """
        delete_bid()
        # obj.delete()

        """
        you can do anything here AFTER deleting the object
        """

        print('==========================delete_model==========================')

class AccountInline(admin.StackedInline):
    readonly_fields = ('id',)
    model = Account
    can_delete = False
    verbose_name_plural = 'Accounts'
    exclude = ['practiceArea', 'demographic', 'licenseNumber', 'underEighteen', 'eighteenToSixtyFive', 'overSixtyFive', 'MSK', 'neuro', 'cardioResp']

class CustomizedUserAdmin(UserAdmin):
    inlines = (AccountInline,)
    list_display = ('username', 'clinic_name', 'first_name', 'last_name', 'user_type')
    search_fields = ['username', 'first_name', 'last_name', 'account__clinicName']

    def clinic_name(self, obj: Account) -> str:
        return obj.account.clinicName

    def user_type(self, obj: Account) -> str:
        return obj.account.userType
        

@admin.register(PracticeAreaType)
class PracticeAreaTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'userType')
    ordering = ('name', )
    search_fields = ('name', 'userType')

class CustomUserAdmin(UserAdmin):
    def __init__(self, *args, **kwargs):
        super(UserAdmin,self).__init__(*args, **kwargs)
        UserAdmin.list_display = list(UserAdmin.list_display) + ['userType']

@admin.register(PopupMessage)
class PopupMessageAdmin(admin.ModelAdmin):
    list_display = ('page', 'message', 'title', 'active', 'show_unauthenticated_users')

@admin.register(MessageAcknowledgement)
class MessageAcknowledgementAdmin(admin.ModelAdmin):
    list_display = ('user', 'popup', 'acknowledged')

admin.site.unregister(User)
admin.site.register(User, CustomizedUserAdmin)
admin.site.register(UserType)
admin.site.register(Demographic)
admin.site.register(DemographicType)
# admin.site.register(PayFrequency)
admin.site.register(PracticeArea)
admin.site.register(ProMember)
admin.site.register(AdminSetting)
admin.site.register(Page)
admin.site.register(PaymentType)
admin.site.register(Number)

def delete_bid(queryset):
    auctionID = queryset[0].auction.auctionID
    queryset.delete()
    min_bid = 999999999
    min_increment = 0
    updated = False
    auction = Auction.objects.get(auctionID=auctionID)
    bids = Bid.objects.filter(auction=auctionID)
    for bid in bids:
        print(bid.amount)
        if bid.amount < min_bid:
            min_bid = bid.amount
    auction.currentLowBid = min_bid

    if min_bid <= 100:
        min_increment = 1
    elif min_bid <= 10000:
        min_increment = 100
    elif min_bid > 25000 and min_bid <= 25000:
        min_increment = 250
    else:
        min_increment = 500

    if min_increment != auction.minimumBidIncrement:
        auction.minimumBidIncrement = min_increment

    auction.save()

from datetime import timedelta
from django.utils import timezone  # Use Django's timezone-aware "now"

def time_diff_from_now(target_datetime):
    now = timezone.now()  # timezone-aware
    if timezone.is_naive(target_datetime):
        # Make the target timezone-aware using current timezone
        target_datetime = timezone.make_aware(target_datetime)

    diff = target_datetime - now
    total_seconds = int(diff.total_seconds())

    if total_seconds < 0:
        total_seconds = abs(total_seconds)
        sign = "-"
    else:
        sign = ""

    days = total_seconds // 86400
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60

    return f"{sign}{days} day{'s' if days != 1 else ''}, {hours} hour{'s' if hours != 1 else ''}, {minutes} minute{'s' if minutes != 1 else ''}"

# Example usage
from datetime import datetime

# If you have a naive datetime
future_time = datetime(2025, 6, 8, 15, 30)  # naive datetime
print(time_diff_from_now(future_time))

