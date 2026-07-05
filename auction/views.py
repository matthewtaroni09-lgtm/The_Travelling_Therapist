from asyncio.format_helpers import _format_args_and_kwargs
import re
from unicodedata import category
import uuid
from wsgiref.simple_server import demo_app
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic import ListView, CreateView
from django.utils import timezone

from The_Travelling_Therapist.settings import ACTIVE_LINK

from django.forms import inlineformset_factory
from .forms import RegisterAcount, AuctionForm, BidForm, UserFormClinic, UserFormTherapist, ProfileUpdateClinic, CreateUserForm, PasswordChangingForm, ContactForm, DemographicForm, PracticeAreaForm, AuctionAccountForm, MessageAcknowledgementForm
import pytz
from django.urls import reverse_lazy
import datetime
from datetime import timedelta
from . import scheduled_tasks
from . import emails
from .models import PROVINCES, Account, AdminSetting, Auction, Bid, Demographic, DemographicType, PracticeArea, PracticeAreaType, User, Account, UserType, PopupMessage, MessageAcknowledgement, Page, PaymentType, Number, Raffle, RaffleEntry, Referral, RaffleTicket
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models.query_utils import Q
from django.db.models import Min, Sum
import json
import requests
import logging
logger = logging.getLogger(__name__)

class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangingForm
    success_url = reverse_lazy('profile')

def contact(request):
    admin = AdminSetting.objects.first()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()

            print(result)
            if result['success'] and result['score'] > .5:
                subject = "Website Inquiry" 
                body = {
                'first_name': form.cleaned_data['first_name'], 
                'last_name': form.cleaned_data['last_name'], 
                'email': form.cleaned_data['email_address'], 
                'message':form.cleaned_data['message'], 
                }
                message = "\n".join(body.values())

                try:
                    if admin.sendEmails:
                        send_mail(subject, message, 'info@travelingtherapist.ca', ['info@travelingtherapist.ca']) 
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                except:
                    HttpResponse('Other email error.')
                return redirect ("index")
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
                logger.warning('****CONTACT US PAGE**** Captcha failure')
                return render(request, "auction/contact_us.html", {})
        else:
            return render(request, "auction/contact_us.html", {'form': form})
    else:
        form = ContactForm(None)
        return render(request, "auction/contact_us.html", {'form': form, 'recaptcha_site_key':settings.GOOGLE_RECAPTCHA_SITE_KEY})

def view_all_auctions(request):
    auctions = ''
    auctions = Auction.objects.filter(active=True).order_by('-auctionEnd') | Auction.objects.filter(closed=True).order_by('-auctionEnd')
    print(auctions)
    return render(request, 'auction/partials/auction_list.html', {'auction': auctions, 'length': len(auctions), 'auction_search': True})

def auction_search(request):
    city = request.POST.get('citySelect')
    payment_type_select = request.POST.get('paymentTypeSelect')
    status_select = request.POST.get('statusSelect')
    clinic_input = request.POST.get('clinicInput')
    search_all_checkbox = request.POST.get('searchAllCheckbox')

    city_fitler = ''
    payment_type_fitler = ''
    status_select_fitler = ''
    clinic_fitler = ''
    type_filter = ''

    # Filter city
    if city == '0':
        city_fitler = Q()
    else:
        city_fitler = Q(clinic__city=city)

    # Filter payment types    
    if payment_type_select == '0':
        payment_type_fitler = Q()
    else:
        payment_type_fitler = Q(paymentTypes__icontains=payment_type_select) | Q(paymentType__name=payment_type_select)

    # Filter statues
    if status_select == '0':
        status_select_fitler = Q()
    else:
        if status_select == 'Active':
            status_select_fitler = Q(active=True)
        elif status_select == 'Closed':
            status_select_fitler = Q(closed=True)
        else:
            status_select_fitler = Q()
    # Filter clinic search
    if clinic_input == '':
        clinic_fitler = Q()
    else:
        clinic_fitler = Q(clinic__clinicName__icontains=clinic_input)

    if request.user.is_authenticated and str(request.user.account.userType) != 'Clinic' and search_all_checkbox != 'on' and not request.user.is_staff:
        type_filter = Q(type=request.user.account.userType)
    else:
        type_filter = Q()

    filter = city_fitler & payment_type_fitler & status_select_fitler & clinic_fitler & type_filter
    # filter = city_fitler & payment_type_fitler & status_select_fitler & clinic_fitler
    print(filter)
    auctions = Auction.objects.filter(filter)
    return render(request, 'auction/partials/auction_list.html', {'auction': auctions, 'length': len(auctions), 'auction_search': True})

def index(request):
    logger.warning('Homepage was accessed at '+str(datetime.datetime.now())+' hours!')
    auction = ''
    if request.user.is_authenticated == False or str(request.user.account.userType) == 'Clinic' or request.user.is_staff:
        auctions = Auction.objects.filter(((Q(active=True)) | (Q(closed=True))) & Q(deleted=False)).order_by('-active', 'auctionEnd')
    elif request.user.is_authenticated == True and request.user.account.userType != 'Clinic':
        auctions = Auction.objects.filter(((Q(active=True)) | (Q(closed=True))) & Q(type=request.user.account.userType)).order_by('-active', 'auctionEnd')
    cities = []
    payment_types = []
    statuses = []
    for auction in auctions:
        if auction.clinic.city not in cities:
            cities.append(auction.clinic.city)
        for payment_type in auction.get_payment_types_list():
            if payment_type not in payment_types:
                payment_types.append(payment_type)
        
        status = ''
        if auction.active:
            status = 'Active'
        elif auction.closed:
            status = 'Closed'
        if status not in statuses:
            statuses.append(status)

    context = {
        'auctions': auctions,
        'cities': cities,
        'payment_types': payment_types,
        'statuses': statuses,
        'auction_search': False,
        'path': 'home'
    }
    return render(request, 'auction/index.html', context)

def terms_and_conditions(request):
    return render(request, 'auction/terms_and_conditions.html', {})

def privacy_policy(request):
    return render(request, 'auction/privacy_policy.html', {})

def test(request):
    return render(request, 'auction/test2.html', {})

def view_user_auctions(request):
    auctions = ''
    user_type = request.user.account.userType
    auctions = Auction.objects.filter(active=True, type=user_type).order_by('-auctionEnd') | Auction.objects.filter(closed=True, type=user_type).order_by('-auctionEnd')
    return render(request, 'auction/partials/auction_list.html', {'auction': auctions})

# Page Links
def about(request):
    return render(request, 'auction/about.html', {'path': 'about'})

def faq(request):
    return render(request, 'auction/faq.html', {'path': 'faq'})

def how_it_works(request):
    return render(request, 'auction/how_it_works.html', {'path': 'how-it-works'})

def mission_vision(request):
    return render(request, 'auction/mission_vision.html', {'path': 'mission-vision'})

def cookie_policy(request):
    return render(request, 'auction/cookie_policy.html', {})

def healthcare_facility_guide(request):
    return render(request, 'auction/healthcare_facility_guide.html', {'path': 'healthcare-facility-guide'})

def clinician_guide(request):
    return render(request, 'auction/clinician_guide.html', {'path': 'clinician-guide'})

def non_traditional_hiring(request):
    return render(request, 'auction/non_traditional_hiring.html', {'path': 'non-traditional-hiring'})

def hospital_guide(request):
    return render(request, 'auction/hospital_guide.html', {'path': 'hospital-guide'})

def LTC_guide(request):
    return render(request, 'auction/LTC_guide.html', {'path': 'LTC-guide'})

def hiring_healthcare_worker(request):
    return render(request, 'auction/hiring_healthcare_worker.html', {'path': 'hiring-healthcare-worker'})

def direct_employer_recruitment(request):
    return render(request, 'auction/direct_employer_recruitment.html', {'path': 'direct-employer-recruitment'})

def headhunter_recruitment(request):
    return render(request, 'auction/headhunter_recruitment.html', {'path': 'headhunter_recruitment'})

def hiring_with_the_traveling_therapist_view(request):
    return render(request, 'auction/hiring_with_the_traveling_therapist.html', {'path': 'hiring-with-the-traveling-therapist'})

def profile(request):
    if request.user.is_authenticated == False:
        return render(request, 'auction/profile.html', {})
    parameter = {}
    show_form = False
    user = request.user
    account = user.account
    
    # Trigger referral verification check
    account.check_and_award_referral()
    
    # Raffle and Referral data
    tickets = account.numTickets  # Sync'd by add_tickets or can use total_tickets property
    joined_raffles = RaffleEntry.objects.filter(user=user).select_related('raffle')
    
    referral_link = account.get_referral_link()
    successful_referrals = account.get_successful_referrals_count()
    ticket_history = RaffleTicket.objects.filter(user=user).order_by('-created_at')

    # Next weekly award date (7-day rolling cooldown)
    now = timezone.now()
    last_award = account.last_ticket_award_date
    if not last_award or (now.date() - last_award).days >= 7:
        parameter['next_award_date'] = now.isoformat() # Available now
    else:
        next_award = last_award + timedelta(days=7)
        # Combine with start of day for a consistent countdown
        next_award_dt = datetime.datetime.combine(next_award, datetime.time.min)
        # Use pytz to ensure the datetime is aware of the project's local timezone
        local_tz = pytz.timezone(settings.TIME_ZONE)
        next_award_dt = local_tz.localize(next_award_dt)
        parameter['next_award_date'] = next_award_dt.isoformat()
    
    # Clinic Profile
    if str(request.user.account.userType).split(' ')[-1] == "Clinic":
        active_raffles = Raffle.objects.filter(active=True, target_audience__in=['Both', 'Clinic'])
        print(request.method)
        # Not closed and not deleted counts any auctions that are active or have no status selected
        active_auctions_list = Auction.objects.filter(active=True, closed=False, deleted=False, clinic=request.user.account)
        past_auctions_list = Auction.objects.filter(active=False, closed=True, deleted=False, clinic=request.user.account)
        pending_auctions_list = Auction.objects.filter(active=False, closed=False, deleted=False, clinic=request.user.account)
        num_pending = pending_auctions_list.count()
        submitted_profile = False
        submitted_auction = False

        if request.method == 'POST':   # This Will Be Run When I Submit My Form. And Possibly Pass New Data.
            user_clinic_form = UserFormClinic(request.POST, instance=request.user)  # request.POST To Pass The POST Data
            profile_clinic_form = ProfileUpdateClinic(request.POST, request.FILES, instance=request.user.account)  # File Data (images) Users Try To Upload.
            print(user_clinic_form.is_valid())
            print(profile_clinic_form.is_valid())
            if user_clinic_form.is_valid() and profile_clinic_form.is_valid():
                user_form = user_clinic_form.save(commit=False)
                user_form.username = user_clinic_form.cleaned_data.get('email')
                user_form.save()
                profile_clinic_form.save()
                # messages.success(request, f'Your profile has been updated!')
                return HttpResponseRedirect('profile')
            else:
                print("fail")
                parameter.update({
                    'active_auctions_list': active_auctions_list,
                    'past_auctions_list': past_auctions_list,
                    'pending_auctions_list': pending_auctions_list,
                    'num_pending': num_pending,
                    'user_clinic_form': user_clinic_form,
                    'profile_clinic_form': profile_clinic_form,
                    'submitted_profile': submitted_profile,
                    'submitted_auction': submitted_auction,
                    'show_form': show_form,
                    'user': user,
                    'tickets': tickets,
                    'joined_raffles': joined_raffles,
                    'active_raffles': active_raffles,
                    'referral_link': referral_link,
                    'successful_referrals': successful_referrals,
                    'ticket_history': ticket_history,
                    'next_award_date': parameter.get('next_award_date')
                })
                return render(request, 'auction/profile.html', parameter)
        else:
            user_clinic_form = UserFormClinic(instance=request.user)
            profile_clinic_form = ProfileUpdateClinic(instance=request.user.account)
            if 'submitted' in request.GET:
                submitted_profile = True
            parameter.update({
                    'active_auctions_list': active_auctions_list,
                    'past_auctions_list': past_auctions_list,
                    'pending_auctions_list': pending_auctions_list,
                    'num_pending': num_pending,
                    'user_clinic_form': user_clinic_form,
                    'profile_clinic_form': profile_clinic_form,
                    'submitted_profile': submitted_profile,
                    'submitted_auction': submitted_auction,
                    'show_form': show_form,
                    'user': user,
                    'tickets': tickets,
                    'joined_raffles': joined_raffles,
                    'active_raffles': active_raffles,
                    'referral_link': referral_link,
                    'successful_referrals': successful_referrals,
                    'ticket_history': ticket_history,
                    'next_award_date': parameter.get('next_award_date')
                })
            return render(request, 'auction/profile.html', parameter)
    # Therapist Profile
    else:
        active_raffles = Raffle.objects.filter(active=True, target_audience__in=['Both', 'Clinician'])
        print(request.method)
        user_id = str(request.user.id)
        active_auctions_list = Bid.objects.raw('SELECT DISTINCT AA.auctionID, AB.bidID, AA.placementStart, AA.placementEnd, AA.clinic_id, AA.currentLowBid, AA.winningPrice, AC.user_id , AC.clinicName, AC.city, AC.province, AC.about, AC.imageOne, AC.imageTwo, UTA.name "type", AA.type_id, count(*) "get_num_bids", CASE WHEN AA.currentLowBid IS NULL THEN "No Bids Yet" WHEN AA.closed = 1 AND AA.active = 0 and AA.winningPrice IS NOT NULL THEN CONCAT("Winning Bid: $", AA.winningPrice) WHEN AA.closed = 1 AND AA.active = 0 and AA.winningPrice IS NULL THEN "No winner" ELSE CONCAT("Current Low Bid: $", AA.currentLowBid) END "get_bid", CASE WHEN UT.name = "Physiotherapy Clinic" THEN "Temporary Physiotherapist" ELSE "" END "get_position_type", PT.name "paymentType" FROM auction_auction AA LEFT JOIN auction_bid AB ON AA.auctionID = AB.auction_id LEFT JOIN auction_account AC ON AA.clinic_id = AC.id LEFT JOIN auction_usertype UT ON AC.userType_id = UT.id JOIN auction_usertype UTA on AA.type_id = UTA.id JOIN auction_paymenttype PT ON AA.paymenttype_id = PT.id WHERE AB.user_id = ' + user_id + ' AND AA.active = 1 AND AA.closed = 0 AND AA.deleted = 0 GROUP BY auctionID, AA.placementStart, AB.amount, AA.placementEnd, AA.clinic_id, AC.user_id , AC.clinicName, AC.city, AC.about, AC.imageOne, AC.imageTwo, UT.name, AA.type_id, PT.name;')
        past_auctions_list = Bid.objects.raw('SELECT DISTINCT AA.auctionID, AB.bidID, AA.placementStart, AA.placementEnd, AA.clinic_id, AA.winningPrice, AC.user_id , AC.clinicName, AC.city, AC.province, AC.about, AC.imageOne, AC.imageTwo, UTA.name "type", AA.type_id, count(*) "get_num_bids", CASE WHEN UT.name = "Physiotherapy Clinic" THEN "Temporary Physiotherapist" ELSE "" END "get_position_type", PT.name "paymentType" FROM auction_auction AA LEFT JOIN auction_bid AB ON AA.auctionID = AB.auction_id LEFT JOIN auction_account AC ON AA.clinic_id = AC.id LEFT JOIN auction_usertype UT ON AC.userType_id = UT.id  JOIN auction_usertype UTA on AA.type_id = UTA.id JOIN auction_paymenttype PT ON AA.paymenttype_id = PT.id WHERE AB.user_id = ' + user_id + ' AND AA.active = 0 AND AA.closed = 1 AND AA.deleted = 0 GROUP BY auctionID, AA.placementStart, AA.placementEnd, AA.clinic_id, AC.user_id , AC.clinicName, AC.city, AC.about, AC.imageOne, AC.imageTwo, UT.name, AA.type_id, PT.name;')
        if request.method == 'POST':
            user_therapist_form = UserFormTherapist(request.POST, instance=request.user)
            if user_therapist_form.is_valid():
                user_form = user_therapist_form.save(commit=False)
                user_form.username = user_therapist_form.cleaned_data.get('email')
                user_form.save()
                # messages.success(request, f'Your profile has been updated!')
                return HttpResponseRedirect('profile')
            else:
                parameter.update({
                    'active_auctions_list': active_auctions_list,
                    'past_auctions_list': past_auctions_list,
                    'user_therapist_form': user_therapist_form,
                    'user': user,
                    'tickets': tickets,
                    'joined_raffles': joined_raffles,
                    'active_raffles': active_raffles,
                    'referral_link': referral_link,
                    'successful_referrals': successful_referrals,
                    'ticket_history': ticket_history,
                    'next_award_date': parameter.get('next_award_date')
                })
                return render(request, 'auction/profile.html', parameter)
        else:
            user_therapist_form = UserFormTherapist(instance=request.user)
            if 'submitted' in request.GET:
                submitted_profile = True
            parameter.update({
                'active_auctions_list': active_auctions_list,
                'past_auctions_list': past_auctions_list,
                'user_therapist_form': user_therapist_form,
                'user': user,
                'tickets': tickets,
                'joined_raffles': joined_raffles,
                'active_raffles': active_raffles,
                'referral_link': referral_link,
                'successful_referrals': successful_referrals,
                'ticket_history': ticket_history,
                'next_award_date': parameter.get('next_award_date')
            })
            return render(request, 'auction/profile.html', parameter)


def view_auction(request, auction_id):
    admin = AdminSetting.objects.first()
    auction = Auction.objects.get(pk=auction_id)
    print(auction.comments)
    num_bids = Bid.objects.filter(auction=auction_id).count()
    num_biders = Bid.objects.values('user').filter(auction=auction_id).distinct().count()
    bids = Bid.objects.filter(auction=auction_id, active=True).annotate(Min('amount')).order_by('amount')
    payment_type = auction.get_primary_payment_type()
    daily_minimum = 0
    if payment_type == 'Fee Split' and auction.assessmentCost != None and auction.assessmentMin != None and auction.treatmentCost != None and auction.treatmentMin != None:
        daily_minimum = (auction.assessmentCost * auction.assessmentMin) + (auction.treatmentCost * auction.treatmentMin)
    else:
        daily_minimum = 0
    auction_change = False
    submitted = False
    max_bid = 0
    assessments = False
    treatments = False

    if auction.assessmentCost is not None and auction.assessmentMin is not None:
        assessments = True
    if auction.treatmentCost is not None and auction.treatmentMin is not None:
        treatments = True

    if num_bids > 0 and auction.currentLowBid is not None and auction.minimumBidIncrement is not None:
        diff = auction.currentLowBid - auction.minimumBidIncrement
        if diff > 0 and diff % auction.minimumBidIncrement == 0:
                max_bid = diff
        elif diff > 0 and diff % auction.minimumBidIncrement != 0:
            max_bid = auction.currentLowBid - (diff % auction.minimumBidIncrement)
    else:
        max_bid = 0

    if request.method == 'POST':
        print('post')
        form = BidForm(request.POST, max_bid=max_bid, min_bid_increment=auction.minimumBidIncrement, payment_type=payment_type)
        print(form.errors)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.auction = auction
            bid.user = request.user
            bid.active = True
            bid.createdBy = request.user
            if auction.currentLowBid is None:
                prev_low_bid = 0
            else:
                prev_low_bid = auction.currentLowBid
            if auction.currentLowBid is not None and bid.amount < auction.currentLowBid:
                auction.currentLowBid = bid.amount
                auction.minimumBidIncrement = set_bid_increment(bid.amount)
                auction_change = True
            if num_bids == 0:
                auction.minimumBidIncrement = set_bid_increment(bid.amount)
                auction.currentLowBid = bid.amount
                auction_change = True
            # A timezone must be specified in order to make the subtraction
            diff = auction.auctionEnd - datetime.datetime.now(pytz.timezone('America/Toronto'))
            if diff.total_seconds() < 60 and (bid.amount <= prev_low_bid or prev_low_bid == 0):
                new_id = str(uuid.uuid4())
                auction.auctionEnd = auction.auctionEnd.astimezone(pytz.timezone('America/Toronto')) + datetime.timedelta(minutes=1)
                scheduled_tasks.print_job()
                try:
                    scheduled_tasks.remove_cron_job(auction.cronID)
                except:
                    print("fail")
                scheduled_tasks.restart(auction.auctionEnd.year, auction.auctionEnd.month, auction.auctionEnd.day, auction.auctionEnd.hour, auction.auctionEnd.minute, auction.auctionEnd.second, new_id, str(auction.auctionID))
                auction.cronID = new_id
                auction_change = True
            if auction_change:
                auction.save()

            # Before saving the new bid get the current lowest bidder from the sorted list of bids if there are existing bids
            if len(bids) > 0:
                current_lowest_bid_user = bids[0].user
            bid.save()

            # Reward the clinician with 5 tickets for placing a bid (only once per listing)
            if hasattr(request.user, 'account'):
                if Bid.objects.filter(user=request.user, auction=auction).count() == 1:
                    request.user.account.add_tickets(5, f"Placed bid on listing {auction.auctionID}")
                    messages.success(request, 'You have earned 5 raffle tickets for placing an offer!', extra_tags='ticket_earned')
                else:
                    messages.success(request, 'Your offer has been successfully placed!')

            # If there are existing bids and the current bid is lower than the current best bid, check if the emails that need to be sent out
            # If the current bid if higher than the current minimum then there is no need to send this email
            if len(bids) > 0 and bid.amount <= auction.currentLowBid:
                check_out_bid(auction.auctionID, bid, request, current_lowest_bid_user, bid.user)
            # Send email to user to thank them for the bid
            if admin.sendEmails:
                try:
                    send_mail(
                        subject = "Thank You for Your Offer - The Traveling Therapist",
                        message = "",
                        html_message = emails.therapist_auction_thank_you_bid(request.user.first_name, request.user.last_name, auction.clinic.clinicName, auction.auctionStart, auction.auctionID),
                        from_email = settings.EMAIL_HOST_USER,
                        # recipient_list = (request.user.email, 'loribine@gmail.com')
                        recipient_list = (request.user.email,)
                    )
                except:
                    print('Thank your for bidding email failed.')
                    logger.warning('Thank your for bidding email failed.')

            return HttpResponseRedirect('/auction/' + str(auction.auctionID))
        else:
            print('else')
            context = {
                'auction': auction,
                'form': form,
                'submitted': submitted,
                'num_bids': num_bids,
                'num_biders': num_biders,
                'payment_type': payment_type,
                'daily_minimum': daily_minimum,
                'assessments': assessments,
                'treatments': treatments
            }
            return render(request, 'auction/view_auction.html', context)
    else:
        form = BidForm(payment_type=payment_type)
        context = {
                'auction': auction,
                'form': form,
                'submitted': submitted,
                'num_bids': num_bids,
                'num_biders': num_biders,
                'payment_type': payment_type,
                'daily_minimum': daily_minimum,
                'assessments': assessments,
                'treatments': treatments
            }
        return render(request, 'auction/view_auction.html', context)
    
def check_out_bid(auction_id, bid, request, current_lowest_bid_user, new_bid_user):
    admin = AdminSetting.objects.first()
    auction = Auction.objects.get(pk=auction_id)
    bids = Bid.objects.filter(auction=auction_id)
    no_email_List = ""
    # Add these two emails so they don't get a second email in the loop
    emailed_list = [current_lowest_bid_user.email, new_bid_user.email]
    count = 0

    print(current_lowest_bid_user, new_bid_user)

    # Email the user that had the lowest bid before the newest bid. If the same user outbids themselves don't send the email
    if admin.sendEmails:
        if current_lowest_bid_user != new_bid_user:
            try:
                print("Outbid user")
                send_mail(
                    subject = "You've been outbid! Place Your Next Offer Now - The Traveling Therapist",
                    message = "",
                    html_message = emails.therapist_auction_outbid_lowest(current_lowest_bid_user.first_name, current_lowest_bid_user.last_name, auction.clinic.clinicName, auction.auctionStart, auction.auctionID),
                    from_email = settings.EMAIL_HOST_USER,
                    # recipient_list = (current_lowest_bid_user.email, 'loribine@gmail.com')
                    recipient_list = (current_lowest_bid_user.email,)
                )
                emailed_list.append(single_bid.user.email)
            except:
                print('Admin email failed to send for the therapist outbid initial low bidder.')
                logger.warning('Admin email failed to send for the therapist outbid initial low bidder.')

    print("START!")
    # Loop through bids and email all other users that there is a new bid. This should not go to the user who just created the bid of the previous lowest bidder since they will get different emails
    for single_bid in bids:
        print("START LOOP")
        print("")
        print(emailed_list)
        print(current_lowest_bid_user.email)
        print("single_bid.user.email: " + str(single_bid.user.email))
        print(count)

        if admin.sendEmails:
            if single_bid.user.email not in emailed_list and count < admin.endAuctionEmailBatchSize:
                # print("Not in email list" + str(single_bid.user.email))
                try:
                    send_mail(
                        subject = "The Traveling Therapist -  A New Lowest Offer Has Been Placed",
                        message = "",
                        html_message = emails.therapist_auction_outbid_all_users(single_bid.user.first_name, single_bid.user.last_name, auction.clinic.clinicName, auction.auctionStart, auction.auctionID),
                        from_email = settings.EMAIL_HOST_USER,
                        # recipient_list = (single_bid.user.email, 'loribine@gmail.com')
                        recipient_list = (single_bid.user.email,)
                    )
                    emailed_list.append(single_bid.user.email)
                    count = count + 1
                    # print("SEND EMAIL: " + str(single_bid.user.email))
                except:
                    # print('Admin email failed to send for the therapist outbid.')
                    logger.warning('Admin email failed to send for the therapist outbid.')
            elif count >= admin.endAuctionEmailBatchSize and single_bid.user.email not in no_email_List and single_bid.user.email not in emailed_list:
                # print("batch Size Reached")
                no_email_List = no_email_List + single_bid.user.email + "<br>"
                count = count + 1
            else:
                print("count = " + str(count))
        # print("**********************************************************************")


    if admin.sendEmails and no_email_List != "":
        try:
            send_mail(
                subject = "ADMIN - Outbid Email Max Reached",
                message = "",
                html_message = "Emails have been sent to outbit users and the limit has been reached. These users did not get the email: <br>" + no_email_List,
                from_email = settings.EMAIL_HOST_USER,
                recipient_list = ('loribine@gmail.com', 'info@travelingtherapist.ca')
        )
        except:
            print('Admin email failed to send for Auction Creation.')
            logger.warning('Admin email failed to send for Auction Creation.')

def get_auction_end(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    practice_area_valid = True

    demographic_obj = Demographic.objects.filter(auction__auctionID = auction_id)
    demographic_type = DemographicType.objects.all()
    demographic_types = []
    demographic_percentages = []

    practice_area_obj = PracticeArea.objects.filter(auction__auctionID = auction_id)
    practice_area_type = PracticeAreaType.objects.filter(userType = auction.type)
    practice_area_types = []
    practice_area_percentages = []

    for obj in demographic_obj:
        demographic_percentages.append(obj.percentage)

    for type in demographic_type:
        demographic_types.append(type.name)

    for obj in practice_area_obj:
        practice_area_percentages.append(obj.percentage)

    for type in practice_area_type:
        practice_area_types.append(type.name)

    # Check to make sure that there are the same number of labels as values
    if len(demographic_percentages) != len(demographic_types):
        demographic_percentages = [0]
        demographic_types = [0]

    # If the user has not entered any practice area pass this to the front-end so the graph is not shown 
    if len(practice_area_obj) == 0:
        practice_area_valid = False

    data = {
        'auctionStart': auction.auctionStart,
        'auctionEnd': auction.auctionEnd,
        'currentLowBid': auction.currentLowBid,
        'clinic': auction.clinic.clinicName,
        'demographic_percentages': demographic_percentages,
        'demographic_types': demographic_types,
        'practice_area_percentages': practice_area_percentages,
        'practice_area_types': practice_area_types,
        'practice_area_valid': practice_area_valid
    }
    return JsonResponse({'data': data})

def check_provinces(request):
    # if the auction is active and the province of the clinic and user do not match show a pop-up
    auction = Auction.objects.get(auctionID=request.GET['auctionID'])
    province_check = True
    if auction.clinic.province != '' or request.user.account.province != '':
        if auction.clinic.province != request.user.account.province and auction.active:
            province_check = False
    else:
        province_check = False
    return JsonResponse({'province_check': province_check})

def get_popups(request): 
    request_page = request.GET['page']
    click_id = request.GET['clickID']
    if click_id == '':
        click_id = None
    page = Page.objects.get(page = request_page)
    user = request.user
    message = ''
    title = ''
    popups = ''
    acknowledged = False
    if request.user.is_authenticated == True:
        popups = PopupMessage.objects.filter(page = page, active = True, clickID = click_id)
    else:
        popups = PopupMessage.objects.filter(page = page, active = True, show_unauthenticated_users = True, clickID = click_id)
    
    print('Popups'+str(popups))

    if popups.count() > 0: 
        for popup in popups:
            try:
                message_acknowledgement = MessageAcknowledgement.objects.get(user = user, popup = popup)
                acknowledged = message_acknowledgement.acknowledged
            except:
                acknowledged = False
            
            # If click_id isn't blank then this refers to a pop-up that is clickable. This pop-up cannot be acknowledged because it is triggered by a click
            if acknowledged == False or click_id != None:
                message = message + " " + popup.message
                title = title + " " + popup.title

    return JsonResponse({'title': title, 'message': message})

def set_acknowledgement(request):
    if request.user.is_authenticated == True:
        request_page = request.POST['page']
        page = Page.objects.get(page = request_page)
        popups = PopupMessage.objects.filter(page = page, active = True)

        for popup in popups:
            message_acknowledgement = MessageAcknowledgement.objects.filter(user=request.user, popup = popup)
            print(message_acknowledgement.count())
            form = ''
            if message_acknowledgement.count() > 0:
                # There should only be one entry per pop-up per user
                form = MessageAcknowledgementForm(request.POST, instance=message_acknowledgement[0])
                print("in count > 0")
                if form.is_valid():
                    acknowledgement = form.save(commit=False)
                    acknowledgement.acknowledged = True
                    acknowledgement.save()
            else:
                form = MessageAcknowledgementForm(request.POST)
                print("in count = 0")
                if form.is_valid():
                    acknowledgement = form.save(commit=False)
                    acknowledgement.user = request.user
                    acknowledgement.popup = popup
                    acknowledgement.acknowledged = True
                    acknowledgement.save()
    return HttpResponse(json.dumps('Success'), content_type="application/json")

def get_all_auctions(request):
    auction_list = list(Auction.objects.filter(Q(active=True) | Q(closed=True)).values())
    return JsonResponse({'data': auction_list})

def get_practice_types(request):
    practice_areas = PracticeAreaType.objects.filter(userType = request.POST['type'])
    max_practice_areas = practice_areas.count()
    practice_area_form_set = inlineformset_factory(Auction, PracticeArea, form=PracticeAreaForm, fields=('category', 'percentage'), max_num=max_practice_areas, extra=max_practice_areas, can_delete=False)
    formset_practice = practice_area_form_set(queryset=PracticeArea.objects.none())
    print(list(practice_areas))
    context = {
        'formset_practice': formset_practice,
        'practice_areas': list(practice_areas)
    }
    return render(request, 'auction/partials/practice_areas.html', context)

def get_active_auctions_clinic(request):
    active_auctions_list = ''
    if str(request.user.account.userType).split(' ')[-1] == "Clinic":
        active_auctions_list = list(Auction.objects.filter(active=True, clinic=request.user.account).values())
    else:
        query = 'SELECT DISTINCT AA.auctionID, AA.auctionStart, AA.auctionEnd, AA.currentLowBid, AB.bidID, AA.placementStart, AA.placementEnd, AA.clinic_id, AC.user_id, AC.clinicName, AC.city, AC.province, AC.about, AC.imageOne, AC.imageTwo, UT.name "userType" FROM auction_auction AA LEFT JOIN auction_bid AB ON AA.auctionID = AB.auction_id LEFT JOIN auction_account AC ON AA.clinic_id = AC.id LEFT JOIN auction_usertype UT ON AC.userType_id = UT.id WHERE AB.user_id = ' + str(request.user.account.user_id) + ' AND AA.active = 1 AND AA.closed = 0 AND AA.deleted = 0 GROUP BY auctionID, AA.placementStart, AA.placementEnd, AA.clinic_id, AC.user_id , AC.clinicName, AC.city, AC.about, AC.imageOne, AC.imageTwo, UT.name;'
        auction_list = Bid.objects.raw(query)
        active_auctions_list = []
        for a in auction_list:
            b = {}
            b.update({'auctionID': a.auctionID, 'auctionStart': a.auctionStart, 'auctionEnd': a.auctionEnd, 'currentLowBid': a.currentLowBid})
            active_auctions_list.append(b)
    return JsonResponse({'data': active_auctions_list})

def get_active_auctions_theraipist(request):
    user_id = str(request.user.id)
    active_auctions_list = list(Bid.objects.raw('SELECT DISTINCT AA.auctionID, AB.bidID, AA.placementStart, AA.placementEnd, AC.clinicName, AC.city, AC.province, AC.about, AC.imageOne, AC.imageTwo, UT.name "userType" FROM auction_auction AA JOIN auction_bid AB ON AA.auctionID = AB.auction_id JOIN auction_account AC ON AA.clinic_id = AC.user_id JOIN auction_usertype UT ON AC.userType_id = UT.id WHERE AB.user_id = ' + user_id + ' AND AA.active = 1 AND AA.closed = 0 AND AA.deleted = 0 GROUP BY auctionID;').values())
    return JsonResponse({'data': active_auctions_list})

def get_view_auction_data(request):
    auction = Auction.objects.get(auctionID=request.GET['auctionID'])
    num_bids = Bid.objects.filter(auction=request.GET['auctionID']).count()
    max_bid = 0
    matchting_types = False
    if num_bids > 0:
        diff = auction.currentLowBid - auction.minimumBidIncrement
        if diff > 0:
            max_bid = diff
        else:
            max_bid = 0
    else:
        max_bid = 0
    if auction.type == request.user.account.userType:
        matchting_types = True
    return JsonResponse({
        'max_bid': max_bid,
        'currentLowBid': auction.currentLowBid,
        'minimumBidIncrement': auction.minimumBidIncrement,
        'auctionEnd': auction.auctionEnd,
        'reservePrice': auction.reservePrice,
        'paymentType': payment_type,
        'active': auction.active,
        'matchtingTypes': matchting_types
    })

def get_demographics(request, clinic_id):
    account = Account.objects.get(pk=clinic_id)
    data = {}
    # data.update({})
    print(account.demographic)
    return JsonResponse({'data': data})

def admin_summary(request):
    accounts_non_staff = Account.objects.filter(user__is_staff=False)
    accounts_staff = Account.objects.filter(user__is_staff=True)
    users_all = User.objects.all()
    auctions = Auction.objects.all()
    bids = Bid.objects.all()
    user_types = UserType.objects.all()
    user_types_count = {}

    print(users_all)

    for type in user_types:
        count = 0
        for account in accounts_non_staff:
            if account.userType == type:
                count = count + 1
        user_types_count[type] = count

    print(user_types_count)
            
    context = {
        'total_users_non_staff': accounts_non_staff.__len__,
        'total_users_staff': accounts_staff.__len__,
        'user_types_count': user_types_count,
        'auction_count': auctions.__len__,
        'bid_count': bids.__len__,
        'users': users_all
    }
    return render(request, 'auction/admin_summary.html', context)

@login_required(login_url='login')
def create_auction(request):
    if request.user.is_authenticated == False:
        return render(request, 'auction/create_auction.html', {})
    admin = AdminSetting.objects.first()
    # Not closed and not deleted counts any auctions that are active or have no status selected
    active_auctions_list = Auction.objects.filter(closed=False, deleted=False, clinic=request.user.account)
    last_auction = Auction.objects.filter(deleted=False, clinic=request.user.account).order_by('-created').first()
    remember_last_auction = Account.objects.filter(user=request.user).values().first()['remember_auction_data']
    submitted_auction = False
    parameter = {}
    selected = ''
    user_types = UserType.objects.filter(~Q(name='Clinic'))
    # If the user has selected remember previous data get their last selected auction type
    if active_auctions_list.count() > 0 and remember_last_auction:
        selected = last_auction.type
    max_auctions = admin
    max_demographics = DemographicType.objects.all().count()
    # Areas of practice are specific to a user type so get the user's type
    max_practice_areas = 0 #PracticeAreaType.objects.all().count()
    demographic_form_set = inlineformset_factory(Auction, Demographic, form=DemographicForm, fields=('category', 'percentage'), max_num=max_demographics, extra=max_demographics, can_delete=False, help_texts=None)
    practice_area_form_set = inlineformset_factory(Auction, PracticeArea, form=PracticeAreaForm, fields=('category', 'percentage'), max_num=max_practice_areas, extra=max_practice_areas, can_delete=False)
    account = Account.objects.get(user=request.user.id)
    if active_auctions_list.count() <= max_auctions.numAllowedAuctions:
        if request.method == "POST":
            form = AuctionForm(request.POST, request.FILES)
            account_form = AuctionAccountForm(request.POST, request.FILES, instance=account)
            formset_demographic = demographic_form_set(queryset=Demographic.objects.none())
            formset_practice = practice_area_form_set(queryset=PracticeArea.objects.none())
            print(form.errors)
            if form.is_valid():
                print('valid form')
                auction = form.save(commit=False)
                auction.clinic = request.user.account
                auction.auctionStart = datetime.datetime.now(pytz.timezone('America/Toronto'))
                auction.auctionEnd = datetime.datetime.now(pytz.timezone('America/Toronto')) + datetime.timedelta(seconds=admin.defaultAuctionLength)
                auction.closed = False
                auction.active = settings.DEFAULT_AUCTION_ACTIVE
                auction.deleted = False
                auction.createdBy = request.user
                auction.modifiedBy = request.user
                auction.auctionNumber = get_next_auction_number()
                print(auction.reservePrice)
                auction.save()
                formset_demographic = demographic_form_set(request.POST, instance=auction, queryset=Demographic.objects.none())
                formset_practice = practice_area_form_set(request.POST, instance=auction, queryset=PracticeArea.objects.none())
                print('AOP')
                
                if formset_practice.is_valid() and formset_demographic.is_valid():
                    formset_demographic.save()
                    # If AOP is populated save it
                    if request.POST.get("AOPPopulated", "") == 'Yes':
                        formset_practice.save()
                else:
                    print("Fail")
                    print(formset_demographic.errors)
                    print(formset_practice.errors)
                    return False

                if account_form.is_valid():
                    account_instance = account_form.save(commit=False)
                    account_instance.user = request.user
                    account_instance.save()
                else:
                    print("Fail")
                    print(account_form.errors)
                    return False
    
                parameter.update({
                'active_auctions_list': active_auctions_list,
                'form': form,
                'account_form': account_form,
                'formset_demographic': formset_demographic,
                'formset_practice': 'formset_practice',
                'submitted_auction': submitted_auction,
                'show_form': True,
                'user_types': user_types,
                'selected': selected
                })
                # return render(request, 'auction/create_auction.html', parameter)

                if admin.sendEmails:
                    # Admin email
                    try:
                        send_mail(
                            subject = "Auction Created - Admin Details",
                            message = "",
                            html_message = emails.auction_created_admin(str(auction.clinic.clinicName), str(auction.clinic.city), str(auction.clinic.province), str(auction.clinic.user.email), str(auction.get_payment_type_label()), str(auction.flatFeeType), str(auction.auctionStart), str(auction.auctionEnd), str(auction.placementStart), str(auction.placementEnd), str(auction.auctionID)),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = ('loribine@gmail.com', 'info@travelingtherapist.ca')
                        )
                    except:
                        print('Admin email failed to send for Listing Creation.')
                        logger.warning('Admin email failed to send for Listing Creation.')


                    # Clinic email
                    try:
                        send_mail(
                            subject = "Your Listing has Been Created",
                            message = "",
                            html_message = emails.clinic_auction_created(str(auction.clinic.clinicName)),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = (auction.clinic.user.email,)
                        )
                    except:
                        print('Healthcare facility email failed to send for Listing Creation.')
                        logger.warning('Healthcare facility email failed to send for Listing Creation.')

                    try:    
                        send_mail(
                            subject = "Your Listing has Been Created",
                            message = "",
                            html_message = "**ADMIN COPY**" + emails.clinic_auction_created(str(auction.clinic.clinicName)),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = ('info@travelingtherapist.ca', )
                        )
                    except:
                        print('Admin copy of healthcare facility email failed to send for Listing Creation.')
                        logger.warning('Admin copy of healthcare facility email failed to send for Listing Creation.')

                scheduled_tasks.start(auction.auctionEnd.year, auction.auctionEnd.month, auction.auctionEnd.day, auction.auctionEnd.hour, auction.auctionEnd.minute, auction.auctionEnd.second, str(auction.auctionID))
                
                # Reward the clinic with 5 tickets for creating a listing
                if hasattr(request.user, 'account'):
                    request.user.account.add_tickets(5, f"Created listing {auction.auctionID}")
                    messages.success(request, 'You have earned 5 raffle tickets for creating a job listing!', extra_tags='ticket_earned')
                
                return HttpResponseRedirect('/profile?submitted=True')
            else:
                print("else")
                parameter.update({
                    'active_auctions_list': active_auctions_list,
                    'form': form,
                    'formset_demographic': formset_demographic,
                    'formset_practice': formset_practice,
                    'submitted_auction': submitted_auction,
                    'show_form': True,
                    'user_types': user_types,
                    'selected': selected
                })
                return render(request, 'auction/create_auction.html', parameter)
        else:
            # New Form
            account_form = AuctionAccountForm(instance=account)
            if remember_last_auction:
                form = AuctionForm(instance=last_auction)
                formset_demographic = demographic_form_set(instance=last_auction)
                formset_practice = practice_area_form_set(instance=last_auction)
            else:
                form = AuctionForm()
                formset_demographic = demographic_form_set(queryset=None)
                formset_practice = practice_area_form_set(queryset=None)
            parameter.update({
                'active_auctions_list': active_auctions_list,
                'form': form,
                'account_form': account_form,
                'formset_demographic': formset_demographic,
                'formset_practice': formset_practice,
                'submitted_auction': submitted_auction,
                'show_form': True,
                'user_types': user_types,
                'selected': selected,
                'remember_last_auction': remember_last_auction
            })
            return render(request, 'auction/create_auction.html', parameter)
    else:
        form = AuctionForm()
        parameter.update({
            'active_auctions_list': active_auctions_list,
            'show_form': False,
            'max_forms': max_auctions.numAllowedAuctions
        })
        return render(request, 'auction/create_auction.html', parameter)

def check_user_payment_type(request):
    user_type = UserType.objects.get(name=request.GET['name'])
    return JsonResponse({
        'feeSplit': user_type.feeSplit
    })

# @login_required(login_url='login')
# @transaction.atomic
def register(request):
    from django.db import transaction
    admin = AdminSetting.objects.first()
    if request.method == 'POST':
        form = RegisterAcount(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    user.refresh_from_db()  # load the profile instance created by the signal
                    
                    # Set user fields
                    user.email = form.cleaned_data.get('username')
                    user.first_name = form.cleaned_data.get('first_name')
                    user.last_name = form.cleaned_data.get('last_name')
                    user.save()

                    # Set account fields
                    account = user.account
                    account.userType = form.cleaned_data.get('user_type')
                    account.city = form.cleaned_data.get('city')
                    account.province = form.cleaned_data.get('province')
                    account.country = 'Canada'
                    account.about = form.cleaned_data.get('about')
                    account.clinicName = form.cleaned_data.get('clinicName')
                    account.imageOne = form.cleaned_data.get('imageOne')
                    account.imageTwo = form.cleaned_data.get('imageTwo')
                    account.imageThree = form.cleaned_data.get('imageThree')
                    account.imageFour = form.cleaned_data.get('imageFour')
                    
                    # Referral logic
                    referral_code = request.session.get('referral_code')
                    if referral_code:
                        print(f"Registration: Found referral code {referral_code} in session")
                        try:
                            referrer_account = Account.objects.get(referral_code=referral_code)
                            referrer = referrer_account.user
                            
                            # Self-referral block
                            if referrer.email != user.email:
                                account.referred_by = referrer
                                # Use get_or_create to prevent IntegrityError on double-submit
                                Referral.objects.get_or_create(referrer=referrer, referred_user=user)
                                print(f"Registration: Referral linked for {user.username} (referred by {referrer.username})")
                            else:
                                print(f"Registration: Self-referral attempt blocked for {user.username}")
                        except Account.DoesNotExist:
                            print(f"Registration: Invalid referral code {referral_code}")
                        # Clean up session
                        del request.session['referral_code']

                    account.save()
                    print(f"Registration: Account saved for {user.username}")

                    # Trigger referral verification check immediately after registration
                    # This awards tickets and sends the referral success email to the referrer
                    awarded = account.check_and_award_referral()
                    print(f"Registration: check_and_award_referral returned {awarded}")
            except Exception as e:
                print(f"Registration Error: Transaction failed: {e}")
                logger.error(f"Registration Error: Transaction failed: {e}")
                # Re-render with form errors if possible, or just re-raise
                return render(request, 'auction/register.html', {'form': form, 'error': 'An internal error occurred. Please try again.'})
            
            # Recaptcha and Emails move OUTSIDE the transaction to prevent rollbacks on network issues
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
            }
            try:
                r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
                result = r.json()
                print(f"Registration: Recaptcha result: {result}")
            except Exception as e:
                print(f"Registration: Recaptcha request failed: {e}")
                result = {'success': True} # Fail open if recaptcha service is down

            if admin.sendEmails:
                print(f"Registration: Attempting to send welcome email to {user.email}")
                if str(account.userType).split(' ')[-1] == "Clinic":
                    # Clinic email
                    try:
                        send_mail(
                                subject = "Welcome to the Traveling Therapist",
                                message = "",
                                html_message = emails.clinic_welcome(account.clinicName),
                                from_email = settings.EMAIL_HOST_USER,
                                recipient_list = [user.email],
                            )
                        print(f"Registration: Welcome email sent to clinic {user.email}")
                    except Exception as e:
                        print(f'Registration Error: Healthcare facility email failed: {e}')
                        logger.warning(f'Registration Error: Healthcare facility email failed: {e}')

                    try:
                        subject_content = "Welcome to the Traveling Therapist"
                        if not result.get('success') or result.get('score', 1.0) <= .5:
                            subject_content = "!!!!Welcome to the Traveling Therapist - POTENTIAL BOT!!!!!"
                        
                        send_mail(
                                subject = subject_content,
                                message = "",
                                html_message = "**ADMIN COPY** " + ("POTENTIAL BOT!!!!!" if "BOT" in subject_content else "") + emails.clinic_welcome(account.clinicName),
                                from_email = settings.EMAIL_HOST_USER,
                                recipient_list = ["info@travelingtherapist.ca"],
                            )
                    except Exception as e:
                        print(f'Registration Error: Admin copy (clinic) failed: {e}')
                else:
                    # Therapist email
                    try:
                        send_mail(
                                subject = "Welcome to the Traveling Therapist",
                                message = "",
                                html_message = emails.therapist_welcome(user.first_name, user.last_name),
                                from_email = settings.EMAIL_HOST_USER,
                                recipient_list = [user.email]
                            )
                        print(f"Registration: Welcome email sent to therapist {user.email}")
                    except Exception as e:
                        print(f'Registration Error: Therapist email failed: {e}')
                        logger.warning(f'Registration Error: Therapist email failed: {e}')

                    try:
                        subject_content = "Welcome to the Traveling Therapist"
                        if not result.get('success') or result.get('score', 1.0) <= .5:
                            subject_content = "!!!!Welcome to the Traveling Therapist - POTENTIAL BOT!!!!!"
                        
                        send_mail(
                                subject = subject_content,
                                message = "",
                                html_message = "**ADMIN COPY** " + ("POTENTIAL BOT!!!!!" if "BOT" in subject_content else "") + emails.therapist_welcome(user.first_name, user.last_name),
                                from_email = settings.EMAIL_HOST_USER,
                                recipient_list = ["info@travelingtherapist.ca"]
                            )
                    except Exception as e:
                        print(f'Registration Error: Admin copy (therapist) failed: {e}')
                    
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request, 'Welcome! You have earned 5 raffle tickets for signing up!', extra_tags='ticket_earned')
            return redirect('index')
        else:
            print("not valid")
            return render(request, 'auction/register.html', {'form': form, 'user_type': form.cleaned_data.get('user_type')})
    else:
        print('outside')
        form = RegisterAcount(None)
        return render(request, 'auction/register.html', {'form': form})
    
# -------------- Login --------------
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('index')
        else:
            messages.error(request, ("Login was unsuccessful. Please check your email and password."))
            return redirect('login')
    else:
        return render(request, 'auction/login.html', {'path': 'login'})

def logout_user(request):
    logout(request)
    # messages.success(request, ("Logged out"))
    return redirect('index')

def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "auction/password/password_reset_email.txt"
					email_template_name_html = "auction/password/password_reset_email.html"
					c = {
					"email":user.email,
					'domain': ACTIVE_LINK,
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
                   
					email = render_to_string(email_template_name, c)
					html_email = render_to_string(email_template_name_html, c)
					try:
						send_mail(subject, email, 'info@travelingtherapist.ca' , [user.email], html_message=html_email, fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("password_reset/done/")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="auction/password/password_reset.html", context={"password_reset_form":password_reset_form})

# -------------- Utility --------------
def set_bid_increment(amount):
    min_increment = 0
    if amount <= 100:
        min_increment = 1
    elif amount > 100 and amount <= 10000:
        min_increment = 100
    elif amount > 10000 and amount <= 25000:
        min_increment = 250
    else:
        min_increment = 500
    return min_increment

def get_next_auction_number():
    number = Number.objects.get(category='auction_id')
    number.currentValue = number.currentValue + 1
    number.save()
    return number.currentValue + 1

# service benefits - static page
def service_benefits_page(request):
    return render(request, 'auction/service_benefits.html', {})

# why use - static page
def what_is_TTT(request):
    return render(request, 'auction/what_is_TTT.html', {})

def hiring_with_the_traveling_therapist_view(request):
    return render(request, 'auction/hiring_with_the_traveling_therapist.html', {})

def retirement_home_hiring_guide(request):
    return render(request, 'auction/retirement_home_hiring_guide.html', {'path': 'retirement-home-hiring-guide'})

def job_boards(request):
    return render(request, 'auction/job_boards.html', {'path': 'job-boards'})

def private_clinic_hiring_guide(request):
    return render(request, 'auction/private_clinic_hiring_guide.html', {'path': 'private-clinic-hiring-guide'})

def agency_comparison(request):
    return render(request, 'auction/agency_comparison.html', {'path': 'agency-comparison'})

def referrals_and_networks(request):
     return render(request, "auction/referrals_and_networks.html", {'path': 'referrals-and-networks'})

def referral_program(request):
    referral_link = ""
    if request.user.is_authenticated:
        referral_link = request.user.account.get_referral_link()
    return render(request, "auction/referral_program.html", {'path': 'facility-referral', 'referral_link': referral_link})

def what_are_raffles(request):
    return render(request, 'auction/what_are_raffles.html', {'path': 'what-are-raffles'})

@login_required(login_url='login')
def surveys(request):
    """
    Role-based surveys page. 
    Redirects unauthenticated users to login (via @login_required(login_url='login')).
    Filters visible surveys based on user type.
    """
    user_type = request.user.account.get_split_user_type()
    context = {
        'user_type': user_type,
        'path': 'surveys'
    }
    return render(request, 'auction/surveys.html', context)

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff)
def admin_raffle_management(request):
    """
    Raffle Management Dashboard for Admins.
    Organizes raffles into Live, Scheduled, and Ended streams.
    Calculates ticket distribution metrics for each raffle.
    """
    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)

    # 1. LIVE RAFFLES: Active, Start in past/present, End in future
    live_raffles_qs = Raffle.objects.filter(
        active=True, 
        startDate__lte=now, 
        endDate__gt=now
    ).order_by('endDate')

    # 2. SCHEDULED RAFFLES: Active, Start in future
    scheduled_raffles_qs = Raffle.objects.filter(
        active=True, 
        startDate__gt=now
    ).order_by('startDate')

    # 3. INACTIVE RAFFLES: Not active, and either haven't ended yet or were never started
    inactive_raffles_qs = Raffle.objects.filter(
        active=False,
        endDate__gt=now
    ).order_by('-startDate')

    # 4. RECENTLY ENDED RAFFLES: End in past, within last 7 days
    ended_raffles_qs = Raffle.objects.filter(
        endDate__lte=now,
        endDate__gte=seven_days_ago
    ).order_by('-endDate')

    def get_raffle_stats(raffles_qs):
        processed = []
        for raffle in raffles_qs:
            entries = RaffleEntry.objects.filter(raffle=raffle).select_related('user__account__userType')
            total_tickets = entries.aggregate(Sum('tickets_added'))['tickets_added__sum'] or 0
            
            clinics_tickets = 0
            clinicians_tickets = 0
            admin_total = 0
            clinics_seen = set()
            clinicians_seen = set()
            sub_breakdown = {} # { 'Physiotherapist': 10, ... }
            clinic_breakdown = {} # { 'Clinic Name A': 5, ... }

            for entry in entries:
                if entry.user.is_superuser or entry.user.is_staff:
                    admin_total += entry.tickets_added
                    continue
                    
                u_type = entry.user.account.userType.name if entry.user.account.userType else "Unknown"
                is_clinic = "Clinic" in u_type
                
                if is_clinic:
                    clinics_tickets += entry.tickets_added
                    clinics_seen.add(entry.user.id)
                    clinic_name = entry.user.account.clinicName
                    if not clinic_name:
                         clinic_name = f"{entry.user.first_name} {entry.user.last_name}".strip()
                    if not clinic_name:
                         clinic_name = entry.user.username
                    clinic_breakdown[clinic_name] = clinic_breakdown.get(clinic_name, 0) + entry.tickets_added
                else:
                    clinicians_tickets += entry.tickets_added
                    clinicians_seen.add(entry.user.id)
                    sub_breakdown[u_type] = sub_breakdown.get(u_type, 0) + entry.tickets_added

            processed.append({
                'obj': raffle,
                'total_tickets': total_tickets,
                'clinics_count': len(clinics_seen),
                'clinics_tickets': clinics_tickets,
                'clinicians_count': len(clinicians_seen),
                'clinicians_total': clinicians_tickets,
                'admin_total': admin_total,
                'sub_breakdown': sub_breakdown,
                'clinic_breakdown': clinic_breakdown,
                'clinics_perc': (clinics_tickets / total_tickets * 100) if total_tickets > 0 else 0,
                'clinicians_perc': (clinicians_tickets / total_tickets * 100) if total_tickets > 0 else 0,
                'admin_perc': (admin_total / total_tickets * 100) if total_tickets > 0 else 0,
            })
        return processed

    context = {
        'path': 'admin-raffle-management',
        'live_raffles': get_raffle_stats(live_raffles_qs),
        'inactive_raffles': get_raffle_stats(inactive_raffles_qs),
        'scheduled_raffles': get_raffle_stats(scheduled_raffles_qs),
        'ended_raffles': get_raffle_stats(ended_raffles_qs),
    }
    return render(request, 'auction/admin_raffle_management.html', context)

@login_required(login_url='login')
@user_passes_test(lambda u: u.is_staff)
def admin_raffle_api(request):
    """
    AJAX API for Raffle CRUD and Administrative Actions.
    Handles both JSON and FormData (for image uploads).
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

    try:
        # Determine how to parse data based on Content-Type
        if request.content_type.startswith('multipart/form-data'):
            data = request.POST
            is_form_data = True
        else:
            data = json.loads(request.body)
            is_form_data = False

        action = data.get('action')
        raffle_id = data.get('raffle_id')

        if action == 'delete':
            raffle = Raffle.objects.get(id=raffle_id)
            if raffle.cronID:
                from . import scheduled_tasks
                try: scheduled_tasks.remove_cron_job(raffle.cronID)
                except: pass
            raffle.delete()
            return JsonResponse({'status': 'success', 'message': 'Raffle deleted successfully.'})

        elif action == 'toggle_status':
            raffle = Raffle.objects.get(id=raffle_id)
            raffle.active = not raffle.active
            raffle.save()
            return JsonResponse({'status': 'success', 'message': f'Raffle {"activated" if raffle.active else "deactivated"} successfully.'})

        elif action == 'force_draw':
            from . import scheduled_tasks
            scheduled_tasks.execute_raffle_draw_task(raffle_id=raffle_id)
            return JsonResponse({'status': 'success', 'message': 'Manual draw executed successfully.'})

        elif action in ['create', 'edit']:
            title = data.get('title')
            description = data.get('description')
            start_date_str = data.get('startDate')
            end_date_str = data.get('endDate')
            tickets_required = data.get('tickets_required', 1)
            target_audience = data.get('target_audience', 'Both')
            value_text = data.get('value_text', '')

            # Parse dates (expecting ISO format from JS)
            from django.utils.dateparse import parse_datetime
            start_date = parse_datetime(start_date_str)
            end_date = parse_datetime(end_date_str)

            if action == 'edit':
                raffle = Raffle.objects.get(id=raffle_id)
            else:
                raffle = Raffle()

            raffle.title = title
            raffle.description = description
            raffle.startDate = start_date
            raffle.endDate = end_date
            raffle.tickets_required = tickets_required
            raffle.target_audience = target_audience
            raffle.value_text = value_text

            # Handle Image Upload if present in request.FILES
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                # Server-side size validation (10MB)
                if image_file.size > 10 * 1024 * 1024:
                    return JsonResponse({'status': 'error', 'message': 'Image file exceeds 10MB limit.'})
                raffle.image = image_file

            raffle.save()

            # Handle cron rescheduling
            from . import scheduled_tasks
            if raffle.cronID:
                try: scheduled_tasks.remove_cron_job(raffle.cronID)
                except: pass
            
            if raffle.active and raffle.endDate:
                scheduled_tasks.start_raffle(raffle.endDate, str(raffle.id))

            return JsonResponse({'status': 'success', 'message': f'Raffle {"updated" if action == "edit" else "created"} successfully.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Unknown action.'})


def join_raffle(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'You must be logged in to enter a raffle.'})
        
        try:
            data = json.loads(request.body)
            raffle_title = data.get('raffle_title')
            tickets_to_add = int(data.get('ticket_count', 0))
            
            if tickets_to_add <= 0:
                return JsonResponse({'status': 'error', 'message': 'Please enter a valid number of tickets.'})
                
            account = request.user.account
            
            # Check balance
            if account.numTickets < tickets_to_add:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'You only have {account.numTickets} tickets available.'
                })
            
            raffle = Raffle.objects.get(title=raffle_title, active=True)

            # MULTIPLIER VALIDATION
            if tickets_to_add % raffle.tickets_required != 0:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'This raffle requires multiples of {raffle.tickets_required} tickets per entry.'
                })
            
            # Deduct tickets via ledger
            account.add_tickets(-tickets_to_add, f"Raffle entry: {raffle.title}")
            
            # Create or update entry
            entry, created = RaffleEntry.objects.get_or_create(
                user=request.user,
                raffle=raffle
            )
            entry.tickets_added += tickets_to_add
            entry.save()
            
            return JsonResponse({
                'status': 'success', 
                'message': f'Successfully added {tickets_to_add} tickets to {raffle.title}.',
                'new_balance': account.numTickets
            })
            
        except Raffle.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Raffle not found or is no longer active.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


# Platform Updates Views
def platform_updates_hub(request):
    return render(request, 'auction/platform_updates_hub.html')

def update_v8_0(request):
    return render(request, 'auction/updates/v8_0.html')

def update_v6_1(request):
    return render(request, 'auction/updates/v6_1.html')

def update_v6_0(request):
    return render(request, 'auction/updates/v6_0.html')

