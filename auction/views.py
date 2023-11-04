from asyncio.format_helpers import _format_args_and_kwargs
import re
from unicodedata import category
import uuid
from wsgiref.simple_server import demo_app
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic import ListView, CreateView

from The_Travelling_Therapist.settings import ACTIVE_LINK

from .filters import AuctionFilter
from .forms import RegisterAcount, AuctionForm, BidForm, UserFormClinic, UserFormTherapist, ProfileUpdateClinic, CreateUserForm, PasswordChangingForm, ContactForm, DemographicForm, PracticeAreaForm, AuctionAccountForm, MessageAcknowledgementForm
from django.urls import reverse_lazy
import datetime
from . import scheduled_tasks
from .models import PROVINCES, Account, AdminSettings, Auction, Bid, Demographic, DemographicType, PracticeArea, PracticeAreaType, User, Account, UserType, PopupMessage, MessageAcknowledgement, Page, PaymentType, Number
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
from django.db.models.query_utils import Q
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from . import emails
from django.core.mail import EmailMessage
from pytz import timezone
from django.core import serializers
from django.contrib import messages # For message alerts
from django.forms import inlineformset_factory
from django.forms import formset_factory
from functools import partial, wraps
from django.http import JsonResponse
import json
import requests

#Test comment

class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangingForm
    success_url = reverse_lazy('profile')

def contact(request):
    admin = AdminSettings.objects.all()[:1].get()
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
            if result['success']:
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
                return redirect ("index")
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
        else:
            return render(request, "auction/contact_us.html", {'form': form})
    else:
        form = ContactForm(None)
        return render(request, "auction/contact_us.html", {'form': form, 'recaptcha_site_key':settings.GOOGLE_RECAPTCHA_SITE_KEY})

def view_all_auctions(request):
    auctions = ''
    auctions = Auction.objects.filter(active=True).order_by('-auctionEnd') | Auction.objects.filter(closed=True).order_by('-auctionEnd')
    return render(request, 'auction/partials/auction_list.html', {'auction': auctions})

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
        payment_type_fitler = Q(paymentType__name=payment_type_select)

    # Filter statues
    if status_select == '0':
        status_select_fitler = Q(active=True)
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

    if request.user.is_authenticated and request.user.account.userType != 'Clinic' and search_all_checkbox != 'on' and not request.user.is_staff:
        type_filter = Q(type=request.user.account.userType)
    else:
        type_filter = Q()
    
    filter = city_fitler & payment_type_fitler & status_select_fitler & clinic_fitler & type_filter
    auctions = Auction.objects.filter(filter)
    return render(request, 'auction/partials/auction_list.html', {'auction': auctions, 'length': len(auctions), 'auction_search': True})

def index(request):
    auction = ''
    if request.user.is_authenticated == False or str(request.user.account.userType) == 'Clinic' or request.user.is_staff:
        auctions = Auction.objects.filter((Q(active=True)) & Q(deleted=False))
    elif request.user.is_authenticated == True and request.user.account.userType != 'Clinic':
        auctions = Auction.objects.filter((Q(active=True) & Q(deleted=False)) & Q(type=request.user.account.userType))
    cities = []
    payment_types = []
    statuses = []
    for auction in auctions:
        if auction.clinic.city not in cities:
            cities.append(auction.clinic.city)
        if auction.paymentType not in payment_types:
            payment_types.append(auction.paymentType)
        
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
        'auction_search': False
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

# class AuctionListView(ListView):
#     model = Auction
#     template_name = 'auction/index.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         # Super users should see all auction types
#         if self.request.user.is_authenticated == True and self.request.user.is_superuser == False:
#             user_type = self.request.user.account.userType
#             if str(user_type) != 'Clinic':
#                 context['filter'] = AuctionFilter(self.request.GET, queryset=Auction.objects.filter(active=True, type=user_type).order_by('-auctionEnd') | Auction.objects.filter(closed=True, type=user_type).order_by('-auctionEnd'))
#             else:
#                 context['filter'] = AuctionFilter(self.request.GET, queryset=Auction.objects.filter(active=True).order_by('-auctionEnd') | Auction.objects.filter(closed=True).order_by('-auctionEnd'))
#         else:
#             context['filter'] = AuctionFilter(self.request.GET, queryset=Auction.objects.filter(active=True).order_by('-auctionEnd') | Auction.objects.filter(closed=True).order_by('-auctionEnd'))
#         return context

# Page Links

def about(request):
    return render(request, 'auction/about.html', {'path': 'about'})

def cookie_policy(request):
    return render(request, 'auction/cookie_policy.html', {})

def profile(request):
    if request.user.is_authenticated == False:
        return render(request, 'auction/profile.html', {})
    parameter = {}
    show_form = False
    user = request.user
    # Clinic Profile
    if str(request.user.account.userType).split(' ')[-1] == "Clinic":
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
                    'user': user
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
                    'user': user
                })
            return render(request, 'auction/profile.html', parameter)
    # Therapist Profile
    else:
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
                    'user': user
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
                'user': user
            })
            return render(request, 'auction/profile.html', parameter)

def view_auction(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    num_bids = Bid.objects.filter(auction=auction_id).count()
    num_biders = Bid.objects.values('user').filter(auction=auction_id).distinct().count()
    payment_type = str(auction.paymentType)
    daily_minimum = 0
    if payment_type == 'Fee Split' and auction.assessmentCost != None and auction.assessmentMin != None and auction.treatmentCost != None and auction.treatmentMin != None:
        daily_minimum = (auction.assessmentCost * auction.assessmentMin) + (auction.treatmentCost * auction.treatmentMin)
    else:
        daily_minimum = 0
    auction_change = False
    submitted = False
    max_bid = 0

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
            if str(auction.paymentType) == 'Fee Split':
                bid.amount = int(request.POST.get("bidSlider", ""))
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
            # A timezone must be specifiedin order to make the subtraction
            diff = auction.auctionEnd - datetime.datetime.now(timezone('America/Toronto'))
            if diff.total_seconds() < 60 and (bid.amount <= prev_low_bid or prev_low_bid == 0):
                new_id = str(uuid.uuid4())
                auction.auctionEnd = auction.auctionEnd.astimezone(timezone('America/Toronto')) + datetime.timedelta(minutes=1)
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
            bid.save()
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
                'daily_minimum': daily_minimum
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
                'daily_minimum': daily_minimum
            }
        return render(request, 'auction/view_auction.html', context)
    
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
        'paymentType': str(auction.paymentType),
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
    auctions = Auction.objects.all()
    bids = Bid.objects.all()
    user_types = UserType.objects.all()
    user_types_count = {}

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
    }
    return render(request, 'auction/admin_summary.html', context)

def create_auction(request):
    if request.user.is_authenticated == False:
        return render(request, 'auction/create_auction.html', {})
    admin = AdminSettings.objects.all()[:1].get()
    # Not closed and not deleted counts any auctions that are active or have no status selected
    active_auctions_list = Auction.objects.filter(closed=False, deleted=False, clinic=request.user.account)
    last_auction = Auction.objects.filter(deleted=False, clinic=request.user.account).order_by('-created').first()
    remember_last_auction = Account.objects.filter(user=request.user).values().first()['remember_auction_data']
    submitted_auction = False
    parameter = {}
    user_types = UserType.objects.filter(~Q(name='Clinic'))
    selected = ''
    # If the user has selected remember previous data get their last selected auction type
    if active_auctions_list.count() > 0 and remember_last_auction:
        selected = last_auction.type
    max_auctions = AdminSettings.objects.all()[0]
    max_demographics = DemographicType.objects.all().count()
    # Areas of practice are specific to a user tpye so get the user's type
    max_practice_areas = 0 #PracticeAreaType.objects.all().count()
    demographic_form_set = inlineformset_factory(Auction, Demographic, form=DemographicForm, fields=('category', 'percentage'), max_num=max_demographics, extra=max_demographics, can_delete=False, help_texts=None)
    practice_area_form_set = inlineformset_factory(Auction, PracticeArea, form=PracticeAreaForm, fields=('category', 'percentage'), max_num=max_practice_areas, extra=max_practice_areas, can_delete=False)
    account = Account.objects.get(user=request.user.id)
    if active_auctions_list.count() <= max_auctions.numAllowedAuctions:
        print("in")
        if request.method == "POST":
            print("POST")
            form = AuctionForm(request.POST, request.FILES)
            account_form = AuctionAccountForm(request.POST, request.FILES, instance=account)
            formset_demographic = demographic_form_set(queryset=Demographic.objects.none())
            formset_practice = practice_area_form_set(queryset=PracticeArea.objects.none())
            print(form.errors)
            if form.is_valid():
                print('valid form')
                auction = form.save(commit=False)
                auction.clinic = request.user.account
                # Check if it is a flat fee or fee split
                if request.POST.get("paymentType", "") == '1':
                    auction.reservePrice = request.POST.get("reservePriceSlider", "")
                print(datetime.datetime.now(timezone('America/Toronto')))
                auction.auctionStart = datetime.datetime.now(timezone('America/Toronto'))
                auction.auctionEnd = datetime.datetime.now(timezone('America/Toronto')) + datetime.timedelta(seconds=admin.defaultAuctionLength)
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
                    send_mail(
                        subject = "Auction Created - Admin Details",
                        message = "",
                        html_message = emails.auction_created_admin(str(auction.clinic.clinicName), str(auction.clinic.city), str(auction.clinic.province), str(auction.clinic.user.email), str(auction.reservePrice), str(auction.auctionStart), str(auction.auctionEnd), str(auction.placementStart), str(auction.placementEnd), str(auction.auctionID)),
                        from_email = settings.EMAIL_HOST_USER,
                        recipient_list = ('loribine@gmail.com', 'info@travelingtherapist.ca')
                    )

                    # Clinic email
                    send_mail(
                        subject = "Your has been Auction Created",
                        message = "",
                        html_message = emails.clinic_auction_created(str(auction.clinic.clinicName)),
                        from_email = settings.EMAIL_HOST_USER,
                        recipient_list = (auction.clinic.user.email, 'info@travelingtherapist.ca')
                    )
                scheduled_tasks.start(auction.auctionEnd.year, auction.auctionEnd.month, auction.auctionEnd.day, auction.auctionEnd.hour, auction.auctionEnd.minute, auction.auctionEnd.second, str(auction.auctionID))
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

# @login_required
# @transaction.atomic
def register(request):
    admin = AdminSettings.objects.all()[:1].get()
    if request.method == 'POST':
        form = RegisterAcount(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.email = form.cleaned_data.get('username')
            user.account.userType = form.cleaned_data.get('user_type')
            user.account.city = form.cleaned_data.get('city')
            user.account.province = form.cleaned_data.get('province')
            user.account.country = 'Canada'
            user.account.about = form.cleaned_data.get('about')
            user.account.clinicName = form.cleaned_data.get('clinicName')
            user.account.imageOne = form.cleaned_data.get('imageOne')
            user.account.imageTwo = form.cleaned_data.get('imageTwo')
            user.account.imageThree = form.cleaned_data.get('imageThree')
            user.account.imageFour = form.cleaned_data.get('imageFour')
            user.save()
            
            if admin.sendEmails:
                if str(user.account.userType).split(' ')[-1] == "Clinic":
                    # Clinic email
                    send_mail(
                            subject = "Welcome to the Traveling Therapist",
                            message = "",
                            html_message = emails.clinic_welcome(user.account.clinicName),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = [user.email],
                        )
                    send_mail(
                            subject = "Welcome to the Traveling Therapist",
                            message = "",
                            html_message = emails.clinic_welcome(user.account.clinicName),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = ["info@travelingtherapist.ca"],
                        )
                else:
                    # Therapist email
                    send_mail(
                            subject = "Welcome to the Traveling Therapist",
                            message = "",
                            html_message = emails.therapist_welcome(user.first_name, user.last_name),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = [user.email]
                        )
                    send_mail(
                            subject = "Welcome to the Traveling Therapist",
                            message = "",
                            html_message = emails.therapist_welcome(user.first_name, user.last_name),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = ["info@travelingtherapist.ca"]
                        )
                    
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
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