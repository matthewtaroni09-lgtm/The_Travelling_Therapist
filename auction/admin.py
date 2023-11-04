from tabnanny import verbose
from unicodedata import category
from django import forms
from django.contrib import admin
from .models import Auction, Bid, Account, PayFrequency, PracticeArea, PracticeAreaType, ProMember, UserType, Demographic, DemographicType, ProMember, AdminSetting, Page, PopupMessage, MessageAcknowledgement, PaymentType, Number
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.conf import settings
from . import emails

class BidInline(admin.TabularInline):
    model = Bid

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    readonly_fields = ('cronID',)
    list_display = ('auctionID', 'auctionNumber', 'clinic', 'paymentType', 'auctionStart', 'auctionEnd', 'active', 'closed', 'placementStart', 'placementEnd', 'winner', 'winningPrice')
    # Reverse alpahbetical order -name
    ordering = ('auctionID', )
    search_fields = ('auctionID',)
    inlines = [BidInline]
    exclude = ['startingBid', 'underEightteen', 'eightteenToSixtyFive', 'overSixtyFive', 'MSK', 'neuro', 'cardioResp', 'payFrequency']

    def save_model(self, request, obj, form, change):
        admin = AdminSettings.objects.all()[:1].get()
        auction = Auction.objects.get(pk=obj.auctionID)
        print("auction = " + str(auction.active))
        print("obj = " + str(obj.active))
        if obj.active and admin.sendEmails and not auction.active:
            send_mail(
                subject = str(obj.clinic.clinicName) + " Your Auction is Live!",
                message = "",
                html_message = emails.clinic_auction_live(str(obj.clinic.clinicName)),
                from_email = settings.EMAIL_HOST_USER,
                recipient_list = (obj.clinic.user.email, 'info@travelingtherapist.ca')
            )
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