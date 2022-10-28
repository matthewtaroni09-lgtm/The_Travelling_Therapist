from tabnanny import verbose
from unicodedata import category
from django import forms
from django.contrib import admin
from .models import Auction, Bid, Account, PayFrequency, PracticeArea, PracticeAreaType, ProMember, UserType, Demographic, DemographicType, ProMember, AdminSettings
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

class BidInline(admin.TabularInline):
    model = Bid

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    readonly_fields = ('cronID',)
    list_display = ('auctionID', 'clinic', 'auctionStart', 'auctionEnd', 'active', 'closed', 'placementStart', 'placementEnd', 'winner', 'winningPrice')
    # Reverse alpahbetical order -name
    ordering = ('auctionID', )
    search_fields = ('auctionID',)
    inlines = [BidInline]
    exclude = ['startingBid', 'underEightteen', 'eightteenToSixtyFive', 'overSixtyFive', 'MSK', 'neuro', 'cardioResp']

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('bidID', 'auction', 'user', 'amount')
    ordering = ('bidID', )
    search_fields = ('bidID', 'auction')

class AccountInline(admin.StackedInline):
    readonly_fields = ('id',)
    model = Account
    can_delete = False
    verbose_name_plural = 'Accounts'
    exclude = ['practiceArea', 'demographic', 'licenseNumber', 'underEighteen', 'eighteenToSixtyFive', 'overSixtyFive', 'MSK', 'neuro', 'cardioResp']

class CustomizedUserAdmin(UserAdmin):
    inlines = (AccountInline,)
    list_display = ('username', 'clinic_name', 'first_name', 'last_name', 'user_type')

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

admin.site.unregister(User)
admin.site.register(User, CustomizedUserAdmin)
admin.site.register(UserType)
admin.site.register(Demographic)
admin.site.register(DemographicType)
admin.site.register(PayFrequency)
admin.site.register(PracticeArea)
admin.site.register(ProMember)
admin.site.register(AdminSettings)