from unicodedata import category
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic import ListView, CreateView

from .filters import AuctionFilter
from .forms import RegisterTherapist, AuctionForm, BidForm, UserForm, ProfileForm
from django.urls import reverse_lazy
import datetime
# from datetime import datetime
from . import scheduled_tasks
from .models import Account, Auction, Bid, PracticeArea, User, Account
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q

class AuctionListView(ListView):
    model = Auction
    template_name = 'auction/filter.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = AuctionFilter(self.request.GET, queryset=self.get_queryset())
        return context

class AuctionListView2(ListView):
    model = Auction
    template_name = 'auction/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = AuctionFilter(self.request.GET, queryset=self.get_queryset())
        return context

# Page Links

def about(request):
    # print("index")
    # scheduled_tasks.update_something('00c0ddbb-505b-4358-872f-315abb1b0db4')
    return render(request, 'auction/about.html', {'path': 'about'})

def profile(request):
    if str(request.user.account.userType).split(' ')[-1] == "Clinic":
        active_auctions_list = Auction.objects.filter(active=True, clinic=request.user.account)
        past_auctions_list = Auction.objects.filter(active=False, deleted=False, clinic=request.user.account)
        submitted = False
        parameter = {}
        if active_auctions_list.count() <= 3:
            if request.method == "POST":
                form = AuctionForm(request.POST, request.FILES)
                if form.is_valid():
                    auction = form.save(commit=False)
                    auction.clinic = request.user.account
                    print('R$ = ' + str(form.cleaned_data.get('reservePrice')))
                    if form.cleaned_data.get('reservePrice') != None:
                        if form.cleaned_data.get('reservePrice') < 10000:
                            auction.minimumBidIncrement = 100
                        elif form.cleaned_data.get('reservePrice') > 10000 and form.cleaned_data.get('reservePrice') < 25000:
                            auction.minimumBidIncrement = 250
                        else:
                            auction.minimumBidIncrement = 500
                    auction.auctionStart = datetime.datetime.now()
                    auction.auctionEnd = datetime.datetime.now() + datetime.timedelta(days=14)
                    auction.currentLowBid = form.cleaned_data.get('reservePrice')
                    auction.closed = False
                    auction.active = False
                    auction.deleted = False
                    auction.createdBy = request.user
                    auction.modifiedBy = request.user
                    auction.save()
                    print(str(auction.auctionEnd.year) + ", " + str(auction.auctionEnd.month) + ", " + str(auction.auctionEnd.day) + ", " + str(auction.auctionEnd.hour) + ", " + str(auction.auctionEnd.minute))
                    print(auction.auctionID)
                    # scheduled_tasks.start(auction.auctionEnd.year, auction.auctionEnd.month, auction.auctionEnd.day, auction.auctionEnd.hour, auction.auctionEnd.minute, str(auction.auctionID))
                    # scheduled_tasks.start(auction.auctionEnd.year, auction.auctionEnd.month, auction.auctionEnd.day, 8, 27, str(auction.auctionID))
                    return HttpResponseRedirect('/profile?submitted=True')
                else:
                    form = AuctionForm
                    if 'submitted' in request.GET:
                        submitted = True

            form = AuctionForm
            parameter.update({
                'active_auctions_list': active_auctions_list,
                'past_auctions_list': past_auctions_list,
                'form': form,
                'submitted': submitted,
                'show_form': True
            })
        else:
            parameter.update({
                'active_auctions_list': active_auctions_list,
                'past_auctions_list': past_auctions_list,
                'show_form': False
            })


        return render(request, 'auction/profile.html', parameter)

    else:
        user_id = str(request.user.id)
        active_auctions_list = Bid.objects.raw('SELECT DISTINCT AA.auctionID, AB.bidID, AA.placementStart, AA.placementEnd, AC.clinicName, AC.city, AC.about, AC.imageOne, AC.imageTwo, UT.name "userType" FROM auction_auction AA JOIN auction_bid AB ON AA.auctionID = AB.auction_id JOIN auction_account AC ON AA.clinic_id = AC.user_id JOIN auction_usertype UT ON AC.userType_id = UT.id WHERE AB.user_id = ' + user_id + ' AND AA.active = 1 AND AA.closed = 0 AND AA.deleted = 0 GROUP BY auctionID;')
        past_auctions_list = Bid.objects.raw('SELECT DISTINCT AA.auctionID, AB.bidID, AA.placementStart, AA.placementEnd, AC.clinicName, AC.city, AC.about, AC.imageOne, AC.imageTwo, UT.name "userType" FROM auction_auction AA JOIN auction_bid AB ON AA.auctionID = AB.auction_id JOIN auction_account AC ON AA.clinic_id = AC.user_id JOIN auction_usertype UT ON AC.userType_id = UT.id WHERE AB.user_id = ' + user_id + ' AND AA.active = 0 AND AA.closed = 1 AND AA.deleted = 0 GROUP BY auctionID;')
        
        return render(request, 'auction/profile.html', {
            'active_auctions_list': active_auctions_list,
            'past_auctions_list': past_auctions_list,
            'path': 'profile'
            # 'form': form,
            # 'submitted': submitted
        })

# def register(request):
#     return render(request, 'auction/register.html', {})

def create_auction(request):
    submitted = False
    if request.method == "POST":
        form = AuctionForm(request.POST, request.FILES)
        if form.is_valid():
            auction = form.save(commit=False)
            auction.clinic = request.user.account
            if form.cleaned_data.get('reservePrice') < 10000:
                auction.minimumBidIncrement = 100
            elif form.cleaned_data.get('reservePrice') > 10000 and form.cleaned_data.get('reservePrice') < 25000:
                auction.minimumBidIncrement = 250
            else:
                auction.minimumBidIncrement = 500
            auction.currentLowBid = form.cleaned_data.get('reservePrice')
            auction.closed = False
            auction.active = True
            auction.deleted = False
            auction.createdBy = request.user
            auction.modifiedBy = request.user
            auction.save()
            print(str(auction.auctionEnd.year) + ", " + str(auction.auctionEnd.month) + ", " + str(auction.auctionEnd.day) + ", " + str(auction.auctionEnd.hour) + ", " + str(auction.auctionEnd.minute))
            print(auction.auctionID)
            # updater.start(auction.auctionEnd.year, auction.auctionEnd.month, auction.auctionEnd.day, auction.auctionEnd.hour, auction.auctionEnd.minute, str(auction.auctionID))
            # return HttpResponseRedirect('/add_auction?submitted=True')
        else:
            form = AuctionForm
            if 'submitted' in request.GET:
                submitted = True

    form = AuctionForm
    return render(request, 'auction/create_auction.html', {'form':form, 'submitted': submitted})

def view_auction(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    num_bids = Bid.objects.filter(auction=auction_id).count()
    num_biders = Bid.objects.values('user').filter(auction=auction_id).distinct().count()

    submitted = False
    form = BidForm(request.POST)
    if form.is_valid():
        bid = form.save(commit=False)
        bid.auction = auction
        bid.user = request.user
        bid.active = True
        bid.createdBy = request.user
        bid.save()
        if bid.amount < auction.currentLowBid:
            auction.currentLowBid = bid.amount
            auction.save()
    else:
        form = BidForm
        if 'submitted' in request.GET:
            submitted = True

    form = BidForm

    return render(request, 'auction/bid-page-2.html',{
        'auction': auction,
        'form': form,
        'submitted': submitted,
        'num_bids': num_bids,
        'num_biders': num_biders
    })

def get_auction_end(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    demogrpahics = {}
    practiceAreas = {}
    for demogrpahic in auction.clinic.demographic.all():
        # JS cannot get a value that starts with a number or has spaces so convert 18 - 65 to words and remove spaces from other categroies
        category = ""
        if demogrpahic.get_category() == "18 - 65":
            category = "eighteenToSixtyFive"
        else:
            category = demogrpahic.get_category().replace(" ", "")
        demogrpahics.update({category: demogrpahic.get_percentage()})

    for practiceArea in auction.clinic.practiceArea.all():
        # JS cannot get a value that has spaces so remove spaces from categroies
        # print(11111 + practiceArea.get_percentage())
        practiceAreas.update({practiceArea.get_category().replace(" ", ""): practiceArea.get_percentage()})

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
    auction_list = list(Auction.objects.filter(active=True).values())
    return JsonResponse({'data': auction_list})

def get_active_auctions_clinic(request):
    active_auctions_list = list(Auction.objects.filter(active=True, clinic=request.user.account).values())
    return JsonResponse({'data': active_auctions_list})

def get_active_auctions_theraipist(request):
    user_id = str(request.user.id)
    active_auctions_list = list(Bid.objects.raw('SELECT DISTINCT AA.auctionID, AB.bidID, AA.placementStart, AA.placementEnd, AC.clinicName, AC.city, AC.about, AC.imageOne, AC.imageTwo, UT.name "userType" FROM auction_auction AA JOIN auction_bid AB ON AA.auctionID = AB.auction_id JOIN auction_account AC ON AA.clinic_id = AC.user_id JOIN auction_usertype UT ON AC.userType_id = UT.id WHERE AB.user_id = ' + user_id + ' AND AA.active = 1 AND AA.closed = 0 AND AA.deleted = 0 GROUP BY auctionID;').values())
    return JsonResponse({'data': active_auctions_list})

def get_demogrpahics(request, clinic_id):
    account = Account.objects.get(pk=clinic_id)
    data = {}
    # data.update({})
    print(account.demographic)
    return JsonResponse({'data': data})

# @login_required
# @transaction.atomic
def register(response):
    print(response.method)
    if response.method == 'POST':
        form = RegisterTherapist(response.POST)
        if form.is_valid():
            print("inside register")
            user = form.save()
            user.refresh_from_db()
            user.account.licenseNumber = form.cleaned_data.get('license_number')
            user.account.city = form.cleaned_data.get('city')
            user.account.userType = form.cleaned_data.get('user_type')
            user.save()
            # username = form.cleaned_data.get('username')
            # password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=password)
            # login(response, user)

            return redirect('index')

        else:
            print("invalid")
            print(form.errors)
            form = RegisterTherapist()
    else:
        form = RegisterTherapist()

    return render(response, 'auction/register.html', {'form': form, 'path': 'register'})

    # if request.method == 'POST':
    #     form = RegisterTherapist(request.POST)
    #     if form.is_valid():
    #         signup = form.save(commit=False)
    #         signup.refresh_from_db()  # load the profile instance created by the signal
    #         signup.email = form.cleaned_data.get('username')

    #         account = Account(signup.id)
    #         # account.userType = 'Physiotherapist'
    #         account.city = form.cleaned_data.get('license_Number')
    #         account.save()
    #         signup.save()
    #         raw_password = form.cleaned_data.get('password1')
    #         signup = authenticate(username=signup.username, password=raw_password)
    #         login(request, signup)
    #         return redirect('index')
    # else:
    #     form = RegisterTherapist()
    # return render(request, 'auction/register.html', {'form': form})


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
            messages.success(request, ("Error logging in"))
            return redirect('login')
    else:
        return render(request, 'auction/login.html', {'path': 'login'})

def logout_user(request):
    logout(request)
    messages.success(request, ("Logged out"))
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
					'domain':'127.0.0.1:8000',
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