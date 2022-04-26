from tabnanny import verbose
from unicodedata import category
from django import forms
from django.contrib import admin
from .models import Auction, Bid, Account, PayFrequency, PracticeArea, PracticeAreaType, ProMember, UserType, Demographic, DemographicType, ProMember
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

class BidInline(admin.TabularInline):
    model = Bid

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = ('auctionID', 'clinic', 'auctionStart', 'auctionEnd', 'reservePrice', 'placementStart', 'placementEnd', 'minimumBidIncrement', 'winner', 'winningPrice')
    # Reverse alpahbetical order -name
    ordering = ('auctionID', )
    search_fields = ('auctionID', 'clinic')
    inlines = [BidInline]

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

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     print("heee" + db_field.name)
    #     if db_field.name == "demographic":
    #         print(request.user)
    #         # print("tttt" + str(self.get_fields('username')))
    #         #print(request.resolver_match.kwargs['object_id'])
    #         kwargs["queryset"] = Demographic.objects.filter(clinic=request.resolver_match.kwargs['object_id'])
    #     return super(AccountInline, self).formfield_for_manytomany(db_field, request, **kwargs)

class CustomizedUserAdmin(UserAdmin):
    inlines = (AccountInline,)


admin.site.unregister(User)
admin.site.register(User, CustomizedUserAdmin)
admin.site.register(UserType)
admin.site.register(Demographic)
admin.site.register(DemographicType)
admin.site.register(PayFrequency)
admin.site.register(PracticeArea)
admin.site.register(PracticeAreaType)
admin.site.register(ProMember)