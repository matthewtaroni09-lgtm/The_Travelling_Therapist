import re
from unicodedata import category
import uuid
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic import ListView, CreateView

from The_Travelling_Therapist.settings import ACTIVE_LINK

from .filters import AuctionFilter
from .forms import RegisterAcount, AuctionForm, BidForm, UserFormClinic, UserFormTherapist, ProfileUpdateClinic, CreateUserForm, PasswordChangingForm, ContactForm, testForm
from django.urls import reverse_lazy
import datetime
# from datetime import datetime
from . import scheduled_tasks
from .models import PROVINCES, Account, AdminSettings, Auction, Bid, PracticeArea, User, Account
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
from pytz import timezone
from django.core import serializers
from django.contrib import messages # For message alerts

def test(request):
    
    if request.method == 'POST':
        details = testForm(request.POST)

        if details.is_valid():
            post = details.save(commit=False)
            post.save()
            return HttpResponse("data saved")
        else:
            return render(request, "auction/test.html", {'form': details})
    else:
        form = testForm(None)
        return render(request, "auction/test.html", {'form': form})


class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangingForm
    success_url = reverse_lazy('profile')

def contact(request):
    admin = AdminSettings.objects.all()[:1].get()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
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
                    send_mail(subject, message, 'loribine@gmail.com', ['loribine@gmail.com']) 
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect ("index")
        else:
            return render(request, "auction/contact_us.html", {'form': form})
    else:
        form = ContactForm(None)
        return render(request, "auction/contact_us.html", {'form': form})

class AuctionListView(ListView):
    model = Auction
    template_name = 'auction/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = AuctionFilter(self.request.GET, queryset=Auction.objects.filter(active=True) | Auction.objects.filter(closed=True))
        return context

# Page Links

def about(request):
    return render(request, 'auction/about.html', {'path': 'about'})

def profile(request):
    if request.user.is_authenticated == False:
        return render(request, 'auction/profile.html', {})
    parameter = {}
    show_form = False
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
                })
            return render(request, 'auction/profile.html', parameter)
    else:
        print(request.method)
        user_id = str(request.user.id)
        active_auctions_list = Bid.objects.raw('SELECT DISTINCT AA.auctionID, AB.bidID, AA.placementStart, AA.placementEnd, AA.clinic_id, AA.currentLowBid, AA.winningPrice, AC.user_id , AC.clinicName, AC.city, AC.province, AC.about, AC.imageOne, AC.imageTwo, UT.name "userType", count(*) "get_num_bids", CASE WHEN AA.currentLowBid IS NULL THEN "No Bids Yet" WHEN AA.closed = 1 AND AA.active = 0 and AA.winningPrice IS NOT NULL THEN CONCAT("Winning Bid: $", AA.winningPrice) WHEN AA.closed = 1 AND AA.active = 0 and AA.winningPrice IS NULL THEN "No winner" ELSE CONCAT("Current Low Bid: $", AA.currentLowBid) END "get_bid", CASE WHEN UT.name = "Physiotherapy Clinic" THEN "Temporary Physiotherapist" ELSE "" END "get_position_type" FROM auction_auction AA LEFT JOIN auction_bid AB ON AA.auctionID = AB.auction_id LEFT JOIN auction_account AC ON AA.clinic_id = AC.id LEFT JOIN auction_usertype UT ON AC.userType_id = UT.id WHERE AB.user_id = ' + user_id + ' AND AA.active = 1 AND AA.closed = 0 AND AA.deleted = 0 GROUP BY auctionID, AA.placementStart, AA.placementEnd, AA.clinic_id, AC.user_id , AC.clinicName, AC.city, AC.about, AC.imageOne, AC.imageTwo, UT.name;')
        past_auctions_list = Bid.objects.raw('SELECT DISTINCT AA.auctionID, AB.bidID, AA.placementStart, AA.placementEnd, AA.clinic_id, AA.winningPrice, AC.user_id , AC.clinicName, AC.city, AC.province, AC.about, AC.imageOne, AC.imageTwo, UT.name "userType", count(*) "get_num_bids", CASE WHEN UT.name = "Physiotherapy Clinic" THEN "Temporary Physiotherapist" ELSE "" END "get_position_type" FROM auction_auction AA LEFT JOIN auction_bid AB ON AA.auctionID = AB.auction_id LEFT JOIN auction_account AC ON AA.clinic_id = AC.id LEFT JOIN auction_usertype UT ON AC.userType_id = UT.id WHERE AB.user_id = ' + user_id + ' AND AA.active = 0 AND AA.closed = 1 AND AA.deleted = 0 GROUP BY auctionID, AA.placementStart, AA.placementEnd, AA.clinic_id, AC.user_id , AC.clinicName, AC.city, AC.about, AC.imageOne, AC.imageTwo, UT.name;')
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
                    'user_therapist_form': user_therapist_form
                })
                return render(request, 'auction/profile.html', parameter)
        else:
            user_therapist_form = UserFormTherapist(instance=request.user)
            if 'submitted' in request.GET:
                submitted_profile = True
            parameter.update({
                'active_auctions_list': active_auctions_list,
                'past_auctions_list': past_auctions_list,
                'user_therapist_form': user_therapist_form
            })
            return render(request, 'auction/profile.html', parameter)

def view_auction(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    num_bids = Bid.objects.filter(auction=auction_id).count()
    num_biders = Bid.objects.values('user').filter(auction=auction_id).distinct().count()
    auction_change = False
    submitted = False
    max_bid = 0

    if num_bids > 0 and auction.currentLowBid is not None and auction.minimumBidIncrement is not None:
        diff = auction.currentLowBid - auction.minimumBidIncrement
        if diff > 0:
            max_bid = diff
        else:
            max_bid = 0
    else:
        max_bid = 0

    if request.method == 'POST':
        form = BidForm(request.POST, max_bid=max_bid, min_bid_increment=auction.minimumBidIncrement)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.auction = auction
            bid.user = request.user
            bid.active = True
            bid.createdBy = request.user
            prev_low_bid = auction.currentLowBid
            if auction.currentLowBid is not None and bid.amount < auction.currentLowBid:
                auction.currentLowBid = bid.amount
                auction.minimumBidIncrement = set_bid_increment(bid.amount)
                auction_change = True
            if num_bids == 0:
                auction.minimumBidIncrement = set_bid_increment(bid.amount)
                auction.currentLowBid = bid.amount
                auction_change = True
            diff = auction.auctionEnd - datetime.datetime.now(timezone('utc'))
            print(diff)
            print(bid.amount)
            print(auction.currentLowBid)
            if diff.total_seconds() < 60 and bid.amount <= prev_low_bid:
                new_id = str(uuid.uuid4())
                auction.auctionEnd = auction.auctionEnd + datetime.timedelta(minutes=1)
                scheduled_tasks.print_job()
                try:
                    scheduled_tasks.remove_cron_job(auction.cronID)
                except:
                    print("fail")
                auctionEndEST = auction.auctionEnd.astimezone(timezone('Canada/Eastern'))
                print(auctionEndEST)
                scheduled_tasks.restart(auctionEndEST.year, auctionEndEST.month, auctionEndEST.day, auctionEndEST.hour, auctionEndEST.minute, auctionEndEST.second, new_id, str(auction.auctionID))
                auction.cronID = new_id
                auction_change = True
            if auction_change:
                auction.save()
            bid.save()
            return HttpResponseRedirect('/auction/' + str(auction.auctionID))
        else:
            context = {
                'auction': auction,
                'form': form,
                'submitted': submitted,
                'num_bids': num_bids,
                'num_biders': num_biders
            }
            return render(request, 'auction/view_auction.html', context)
    else:
        form = BidForm(None)
        context = {
                'auction': auction,
                'form': form,
                'submitted': submitted,
                'num_bids': num_bids,
                'num_biders': num_biders
            }
        return render(request, 'auction/view_auction.html', context)
    
def get_auction_end(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    account = Account.objects.get(user=auction.clinic.user)
    demogrpahics = {}
    practiceAreas = {}

    demogrpahics.update({'Under18': account.underEighteen})
    demogrpahics.update({'eighteenToSixtyFive': account.eighteenToSixtyFive})
    demogrpahics.update({'Over65': account.overSixtyFive})
    practiceAreas.update({'MSK': account.MSK})
    practiceAreas.update({'Neuro': account.neuro})
    practiceAreas.update({'CardioResp': account.cardioResp})

    data = {
        'auctionStart': auction.auctionStart,
        'auctionEnd': auction.auctionEnd,
        'currentLowBid': auction.currentLowBid,
        'clinic': auction.clinic.clinicName,
        'demogrpahics': demogrpahics,
        'practiceAreas': practiceAreas
    }
    return JsonResponse({'data': data})

def get_all_auctions(request):
    auction_list = list(Auction.objects.filter(Q(active=True) | Q(closed=True)).values())
    return JsonResponse({'data': auction_list})

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
    if num_bids > 0:
        diff = auction.currentLowBid - auction.minimumBidIncrement
        if diff > 0:
            max_bid = diff
        else:
            max_bid = 0
    else:
        max_bid = 0
    print(max_bid)
    return JsonResponse({
        'max_bid': max_bid,
        'currentLowBid': auction.currentLowBid,
        'minimumBidIncrement': auction.minimumBidIncrement,
        'auctionEnd': auction.auctionEnd
        })

def get_demogrpahics(request, clinic_id):
    account = Account.objects.get(pk=clinic_id)
    data = {}
    # data.update({})
    print(account.demographic)
    return JsonResponse({'data': data})

def create_auction(request):
    if request.user.is_authenticated == False:
        return render(request, 'auction/create_auction.html', {})
    admin = AdminSettings.objects.all()[:1].get()
    # Not closed and not deleted counts any auctions that are active or have no status selected
    active_auctions_list = Auction.objects.filter(closed=False, deleted=False, clinic=request.user.account)
    submitted_auction = False
    parameter = {}
    max_auctions = AdminSettings.objects.all()[0]
    print(active_auctions_list.count())
    if active_auctions_list.count() <= max_auctions.numAllowedAuctions:
        if request.method == "POST":
            form = AuctionForm(request.POST, request.FILES)
            if form.is_valid():
                auction = form.save(commit=False)
                auction.clinic = request.user.account
                auction.auctionStart = datetime.datetime.now(timezone('US/Eastern'))
                auction.auctionEnd = datetime.datetime.now(timezone('US/Eastern')) + datetime.timedelta(seconds=settings.DEAFULT_AUCTION_LENGTH)
                auction.closed = False
                auction.active = settings.DEFAULT_AUCTION_ACTIVE
                auction.deleted = False
                auction.createdBy = request.user
                auction.modifiedBy = request.user
                auction.save()
                if admin.sendEmails:
                    # Therapist email
                    send_mail(
                        subject = "Auction Created",
                        message = "",
                        html_message = emails.auction_created_admin(str(auction.clinic.clinicName), str(auction.clinic.city), str(auction.clinic.province), str(auction.clinic.user.email), str(auction.reservePrice), str(auction.auctionStart), str(auction.auctionEnd), str(auction.placementStart), str(auction.placementEnd), str(auction.auctionID)),
                        from_email = settings.EMAIL_HOST_USER,
                        recipient_list = ('loribine@gmail.com', 'info@travelingtherapist.ca')
                    )
                print(str(auction.auctionEnd.year) + ", " + str(auction.auctionEnd.month) + ", " + str(auction.auctionEnd.day) + ", " + str(auction.auctionEnd.hour) + ", " + str(auction.auctionEnd.minute))
                print(auction.auctionID)
                scheduled_tasks.start(auction.auctionEnd.year, auction.auctionEnd.month, auction.auctionEnd.day, auction.auctionEnd.hour, auction.auctionEnd.minute, auction.auctionEnd.second, str(auction.auctionID))
                return HttpResponseRedirect('/profile?submitted=True')
            else:
                # if 'submitted' in request.GET:
                #     submitted_auction = True
                parameter.update({
                    'active_auctions_list': active_auctions_list,
                    'form': form,
                    'submitted_auction': submitted_auction,
                    'show_form': True
                })
                return render(request, 'auction/create_auction.html', parameter)
        else:
            form = AuctionForm(None)
            parameter.update({
                'active_auctions_list': active_auctions_list,
                'form': form,
                'submitted_auction': submitted_auction,
                'show_form': True
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
            user.account.underEighteen = form.cleaned_data.get('underEighteen')
            user.account.eighteenToSixtyFive = form.cleaned_data.get('eighteenToSixtyFive')
            user.account.overSixtyFive = form.cleaned_data.get('overSixtyFive')
            user.account.MSK = form.cleaned_data.get('MSK')
            user.account.neuro = form.cleaned_data.get('neuro')
            user.account.cardioResp = form.cleaned_data.get('cardioResp')
            user.save()
            
            if admin.sendEmails:
                if str(user.account.userType).split(' ')[-1] == "Clinic":
                    # Clinic email
                    send_mail(
                            subject = "Welcome to the Traveling Therapist",
                            message = "",
                            html_message = emails.clinic_welcome(user.account.clinicName),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = [user.email]
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
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('index')
        else:
            print("not valid")
            return render(request, 'auction/register.html', {'form': form})
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
						send_mail(subject, email, 'admin@example.com' , [user.email], html_message=html_email, fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("password_reset/done/")
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="auction/password/password_reset.html", context={"password_reset_form":password_reset_form})

# -------------- Utility --------------
def set_bid_increment(reservePrice):
    min_increment = 0
    if reservePrice <= 15000:
        min_increment = 100
    elif reservePrice > 15000 and reservePrice <= 50000:
        min_increment = 250
    else:
        min_increment = 500
    return min_increment