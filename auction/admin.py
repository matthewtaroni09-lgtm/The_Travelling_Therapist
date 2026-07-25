from decimal import Decimal
from tabnanny import verbose
from unicodedata import category
from django import forms
from django.contrib import admin
from django.contrib import messages
from django.http import BadHeaderError, HttpResponse
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html, format_html_join
from django.db import models as django_models
from .models import Auction, Bid, Account, PayFrequency, PracticeArea, PracticeAreaType, ProMember, UserType, Demographic, DemographicType, ProMember, AdminSetting, Page, PopupMessage, MessageAcknowledgement, PaymentType, Number, Raffle, RaffleEntry, Referral, RaffleTicket
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
from django.conf import settings
from . import emails
from .forms import AuctionForm, AuctionAdminForm
from . import scheduled_tasks
from The_Travelling_Therapist.settings import ENVIRONMENT, DEV_LINK, PROD_LINK
from datetime import datetime, timedelta
import time

class BidInline(admin.TabularInline):
    model = Bid
    ordering = ('amount',)
    verbose_name = 'Offer'
    verbose_name_plural = 'Offers'
    show_change_link = True

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    form = AuctionAdminForm
    changelist_template = 'admin/auction/auction/change_list.html'
    change_form_template = 'admin/auction/auction/change_form.html'
    save_on_top = True
    readonly_fields = ('auctionID', 'cronID', 'required_skills_display', 'negotiable_perks_display', 'created', 'modified')
    list_display = ('auction_number_admin', 'listing_view_link', 'status_display', 'clinic_display', 'payment_type_label', 'desired_offer_guidance', 'minimum_compensation_display', 'required_skills_count', 'negotiable_perks_count', 'auctionStart', 'auctionEnd', 'placementStart', 'placementEnd', 'winner', 'winning_offer_display_admin')
    list_display_links = ('auction_number_admin',)
    # Reverse alpahbetical order -name
    ordering = ('-auctionNumber', )
    search_fields = ('auctionID', 'auctionNumber', 'clinic__clinicName', 'clinic__user__email', 'winner__username', 'winner__email')
    inlines = [BidInline]
    exclude = ['startingBid', 'underEightteen', 'eightteenToSixtyFive', 'overSixtyFive', 'MSK', 'neuro', 'cardioResp', 'payFrequency', 'paymentType']
    fieldsets = (
        ('Quick Action', {
            'fields': ('auctionID', 'auctionNumber', 'clinic', 'type', 'comments', 'listing_status'),
        }),
        ('Listing Dates and Schedule', {
            'fields': (
                ('auctionStart', 'auctionEnd'),
                ('placementStart', 'placementEnd'),
                ('mondayStart', 'mondayEnd'),
                ('tuesdayStart', 'tuesdayEnd'),
                ('wednesdayStart', 'wednesdayEnd'),
                ('thursdayStart', 'thursdayEnd'),
                ('fridayStart', 'fridayEnd'),
                ('saturdayStart', 'saturdayEnd'),
                ('sundayStart', 'sundayEnd'),
            ),
        }),
        ('Offer Settings', {
            'fields': ('paymentTypes', 'paymentTypesSelection', 'flatFeeType', 'desiredFeeSplitPercentage', 'minimumCompensation', 'desiredFlatFeeHourly', 'desiredFlatFeeTotalContract', 'winner', 'winningPrice'),
        }),
        ('Skills and Perks', {
            'fields': ('required_skills_display', 'negotiable_perks_display'),
        }),
        ('Nice to Know', {
            'fields': ('createdBy', 'modified', 'modifiedBy'),
        }),
    )

    def auction_number_admin(self, obj):
        return f'#{obj.auctionNumber}' if obj.auctionNumber is not None else '-'

    auction_number_admin.short_description = 'Listing #'
    auction_number_admin.admin_order_field = 'auctionNumber'

    def listing_view_link(self, obj):
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer">View</a>', reverse('auction', args=[obj.auctionID]))

    listing_view_link.short_description = 'Listing'

    def clinic_display(self, obj):
        username = getattr(obj.clinic.user, 'username', '')
        email = getattr(obj.clinic.user, 'email', '')
        return f'{username} ({email})' if username or email else str(obj.clinic)

    clinic_display.short_description = 'Facility Username (Email)'

    def status_display(self, obj):
        change_url = reverse('admin:auction_auction_change', args=[obj.pk])
        if obj.deleted:
            return format_html(
                '<button type="button" class="ttt-status-open" style="color:#111827;font-weight:600;text-decoration:underline;" data-auction-id="{}" data-current-status="deleted" data-current-status-label="Deleted" data-change-url="{}">Deleted</button>',
                obj.pk,
                change_url,
            )
        if getattr(obj, 'waitingCloseout', False) and not obj.closed:
            return format_html(
                '<button type="button" class="ttt-status-open" style="color:#f0ad4e;font-weight:600;text-decoration:underline;" data-auction-id="{}" data-current-status="waiting" data-current-status-label="Closed (Waiting)" data-change-url="{}">Closed (Waiting)</button>',
                obj.pk,
                change_url,
            )
        if obj.closed or obj.is_effectively_closed():
            return format_html(
                '<button type="button" class="ttt-status-open" style="color:#dc3545;font-weight:600;text-decoration:underline;" data-auction-id="{}" data-current-status="closed" data-current-status-label="Closed" data-change-url="{}">Closed</button>',
                obj.pk,
                change_url,
            )
        if obj.active:
            return format_html(
                '<button type="button" class="ttt-status-open" style="color:#198754;font-weight:600;text-decoration:underline;" data-auction-id="{}" data-current-status="active" data-current-status-label="Active" data-change-url="{}">Active</button>',
                obj.pk,
                change_url,
            )
        return format_html(
            '<button type="button" class="ttt-status-open" style="color:#f0ad4e;font-weight:600;text-decoration:underline;" data-auction-id="{}" data-current-status="pending" data-current-status-label="Pending" data-change-url="{}">Pending</button>',
            obj.pk,
            change_url,
        )

    status_display.short_description = 'Status'

    def winning_offer_display_admin(self, obj):
        return obj.get_winning_offer_display() if obj.winner_id is not None else 'None'

    winning_offer_display_admin.short_description = 'Winning Offer'

    def payment_type_label(self, obj):
        return obj.get_payment_type_label()

    payment_type_label.short_description = 'Payment Types'

    def desired_offer_guidance(self, obj):
        guidance = []
        if obj.desiredFeeSplitPercentage is not None:
            guidance.append(f"Fee Split: {obj.desiredFeeSplitPercentage}%")
        if obj.desiredFlatFeeHourly is not None:
            guidance.append(f"Hourly: ${Decimal(obj.desiredFlatFeeHourly):.2f}/hr")
        if obj.desiredFlatFeeTotalContract is not None:
            guidance.append(f"TCP: ${Decimal(obj.desiredFlatFeeTotalContract):.2f}")
        return ' | '.join(guidance) if guidance else 'None'

    desired_offer_guidance.short_description = 'Desired Offer'

    def minimum_compensation_display(self, obj):
        return f"${obj.minimumCompensation}" if obj.minimumCompensation is not None else 'None'

    minimum_compensation_display.short_description = 'Min Comp'

    def required_skills_count(self, obj):
        return len(obj.get_required_skill_rows())

    required_skills_count.short_description = 'Skills #'

    def negotiable_perks_count(self, obj):
        return len(obj.get_public_perk_rows())

    negotiable_perks_count.short_description = 'Perks #'

    def required_skills_display(self, obj):
        rows = obj.get_required_skill_rows()
        if len(rows) == 0:
            return 'None'

        required_items = [row['name'] for row in rows if str(row.get('requirement', '')).lower() == 'required']
        preferred_items = [row['name'] for row in rows if str(row.get('requirement', '')).lower() != 'required']

        required_html = format_html_join('', '<li>{}</li>', ((item,) for item in required_items)) if required_items else format_html('<li>-</li>')
        preferred_html = format_html_join('', '<li>{}</li>', ((item,) for item in preferred_items)) if preferred_items else format_html('<li>-</li>')

        return format_html(
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:840px;">'
            '<div style="border:1px solid #d7dce2;border-radius:6px;padding:8px;">'
            '<p style="margin:0 0 6px;font-weight:600;">Required</p>'
            '<ul style="margin:0;padding-left:18px;">{}</ul>'
            '</div>'
            '<div style="border:1px solid #d7dce2;border-radius:6px;padding:8px;">'
            '<p style="margin:0 0 6px;font-weight:600;">Preferred</p>'
            '<ul style="margin:0;padding-left:18px;">{}</ul>'
            '</div>'
            '</div>',
            required_html,
            preferred_html,
        )

    required_skills_display.short_description = 'Required Skills Summary'

    def negotiable_perks_display(self, obj):
        rows = obj.get_private_perk_rows()
        if len(rows) == 0:
            return 'None'

        row_tuples = []
        for row in rows:
            amount_text = f"${row['amount']}" if row.get('amount', 0) > 0 else 'N/A'
            details_text = row.get('details') or '-'
            row_tuples.append((row['name'], amount_text, details_text))

        body_html = format_html_join(
            '',
            '<tr>'
            '<td style="padding:6px 8px;border-top:1px solid #d7dce2;">{}</td>'
            '<td style="padding:6px 8px;border-top:1px solid #d7dce2;">{}</td>'
            '<td style="padding:6px 8px;border-top:1px solid #d7dce2;">{}</td>'
            '</tr>',
            row_tuples,
        )

        return format_html(
            '<div style="overflow-x:auto;max-width:840px;">'
            '<table style="width:100%;border:1px solid #d7dce2;border-radius:6px;border-collapse:separate;border-spacing:0;">'
            '<thead>'
            '<tr>'
            '<th style="text-align:left;padding:7px 8px;">Perk</th>'
            '<th style="text-align:left;padding:7px 8px;">Value</th>'
            '<th style="text-align:left;padding:7px 8px;">Description</th>'
            '</tr>'
            '</thead>'
            '<tbody>{}</tbody>'
            '</table>'
            '</div>',
            body_html,
        )

    negotiable_perks_display.short_description = 'Negotiable Perks Summary'

    def save_model(self, request, obj, form, change):
        listing_status = form.cleaned_data.get('listing_status') if hasattr(form, 'cleaned_data') else ''
        if listing_status == 'deleted':
            obj.active = False
            obj.waitingCloseout = False
            obj.closed = False
            obj.deleted = True
        elif listing_status == 'waiting':
            obj.active = False
            obj.waitingCloseout = True
            obj.closed = False
            obj.deleted = False
        elif listing_status == 'closed':
            obj.active = False
            obj.waitingCloseout = False
            obj.closed = True
            obj.deleted = False
        elif listing_status == 'active':
            obj.active = True
            obj.waitingCloseout = False
            obj.closed = False
            obj.deleted = False
        else:
            obj.active = False
            obj.waitingCloseout = False
            obj.closed = False
            obj.deleted = False

        admin = AdminSetting.objects.first()
        waiting_closeout_job_id = f'{obj.auctionID}_waiting_closeout'
        if listing_status == 'waiting' and obj.auctionEnd is not None:
            waiting_seconds = admin.defaultClosedWaitingPeriodLength if admin is not None else 604800
            scheduled_tasks.schedule_waiting_closeout(obj.auctionID, obj.auctionEnd + timedelta(seconds=waiting_seconds))
        else:
            scheduled_tasks.remove_cron_job(waiting_closeout_job_id)

        auction = Auction.objects.filter(pk=obj.auctionID).first()
        previous_active = auction.active if auction is not None else False
        print("auction = " + str(previous_active))
        print("obj = " + str(obj.active))

        # Query the user list for users that are the same type as the auction
        current_auction = auction or obj
        print(current_auction.type)
        accounts = Account.objects.filter(userType=current_auction.type)
        print(accounts)

        if obj.active and admin.sendEmails and not previous_active:
            try:
                send_mail(
                    subject = str(obj.clinic.clinicName) + " Your Listing is Live!",
                    message = "",
                    html_message = emails.clinic_auction_live(str(obj.clinic.clinicName)),
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list = (obj.clinic.user.email,)
                )
            except BadHeaderError:
                    return HttpResponse('Invalid header found.')
            
            try:
                send_mail(
                    subject = str(obj.clinic.clinicName) + " Your Listing is Live!",
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
                link = DEV_LINK + "/auction/" + str(current_auction.auctionID)
            else:
                link = PROD_LINK + "/auction/" + str(current_auction.auctionID)

            clinic_city = current_auction.clinic.city or ""
            clinic_province = current_auction.clinic.province or ""
            clinic_location = clinic_city
            if clinic_province:
                clinic_location = clinic_city + ", " + clinic_province

            email_count = 0
            admin_setting = AdminSetting.objects.first()
            batch_size = admin_setting.endAuctionEmailBatchSize

            for account in accounts:
                print(current_auction.get_payment_type_label())
                if email_count < batch_size:
                    try:
                        send_mail(
                            subject = "NEW LISTING - The Traveling Therapist",
                            message = "",
                            html_message = emails.new_auction_email_to_all(account.user.first_name, account.user.last_name, link, str(current_auction.placementStart), str(current_auction.placementEnd), current_auction.get_payment_type_label(), current_auction.clinic.clinicName, clinic_location, time_diff_from_now(current_auction.auctionEnd)),
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('update-status/', self.admin_site.admin_view(self.update_status_view), name='auction_auction_update_status'),
        ]
        return custom_urls + urls

    def update_status_view(self, request):
        if request.method != 'POST':
            messages.error(request, 'Invalid request.')
            return redirect('admin:auction_auction_changelist')

        auction_id = request.POST.get('auction_id')
        listing_status = request.POST.get('listing_status', '')
        auction = Auction.objects.get(pk=auction_id)

        dummy_form = type('StatusForm', (), {'cleaned_data': {'listing_status': listing_status}})()
        self.save_model(request, auction, dummy_form, change=True)
        messages.success(request, f'Listing #{auction.auctionNumber} status updated.')
        return redirect(request.META.get('HTTP_REFERER') or reverse('admin:auction_auction_changelist'))

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('bidID', 'auction', 'user', 'offerType', 'amount', 'submissionGroup')
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
    fk_name = 'user'
    can_delete = False
    verbose_name_plural = 'Accounts'
    exclude = ['practiceArea', 'demographic', 'licenseNumber', 'underEighteen', 'eighteenToSixtyFive', 'overSixtyFive', 'MSK', 'neuro', 'cardioResp']

@admin.register(Raffle)
class RaffleAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_audience', 'active', 'startDate', 'endDate', 'winner', 'numWinningTickets')
    search_fields = ('title',)
    list_filter = ('active', 'target_audience')
    readonly_fields = ('cronID',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.active and obj.endDate:
            from . import scheduled_tasks
            # Remove existing job if it exists
            if obj.cronID:
                try:
                    scheduled_tasks.remove_cron_job(obj.cronID)
                except:
                    pass
            
            # Schedule new job
            scheduled_tasks.start_raffle(obj.endDate, str(obj.id))

@admin.register(RaffleEntry)
class RaffleEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'raffle', 'tickets_added', 'created')
    search_fields = ('user__username', 'raffle__title')

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
admin.site.register(Referral)
admin.site.register(RaffleTicket)

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

def time_diff_from_now(target_datetime):
    from django.utils import timezone
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
