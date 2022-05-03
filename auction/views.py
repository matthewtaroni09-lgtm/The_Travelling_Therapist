from unicodedata import category
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic import ListView, CreateView

from .filters import AuctionFilter
from .forms import RegisterTherapist, AuctionForm, BidForm
from django.urls import reverse_lazy
import datetime
from datetime import datetime

from .models import Account, Auction, Bid, PracticeArea, User, Account

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
def index(request):
    auctions_list = Auction.objects.filter(active=True)
    location_list = []
    therapist_list = []
    for auction in auctions_list:
        if auction.clinic.city not in location_list:
            location_list.append(auction.clinic.city)

        if auction.clinic.userType not in therapist_list:
            therapist_list.append(auction.clinic.userType)

    return render(request, 'auction/index.html', {
        'auctions_list': auctions_list,
        'location_list': location_list,
        'therapist_list': therapist_list
    })

def about(request):
    return render(request, 'auction/about.html', {})

def profile(request):
    active_auctions_list = Auction.objects.filter(active=True, clinic=request.user.account)
    past_auctions_list = Auction.objects.filter(active=False, deleted=False, clinic=request.user.account)

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

    return render(request, 'auction/profile.html', {
        'active_auctions_list': active_auctions_list,
        'past_auctions_list': past_auctions_list,
        'form': form,
        'submitted': submitted
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
    form = BidForm(request.POST)

    num_bids = Bid.objects.filter(auction=auction_id).count()
    num_biders = Bid.objects.values('user').filter(auction=auction_id).distinct().count()

    return render(request, 'auction/bid-page-2.html',{
        'auction': auction,
        'form': form,
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

def get_demogrpahics(request, clinic_id):
    account = Account.objects.get(pk=clinic_id)
    data = {}
    # data.update({})
    print(account.demographic)
    return JsonResponse({'data': data})

def register_therapist(request):
    if request.method == 'POST':
        form = RegisterTherapist(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            id_number = form.cleaned_data['license_number']

            

            id_model = Account(user.id)
            id_model.user = user
            id_model.licenseNumber = id_number

            id_model.save()
            user.save()

            return HttpResponseRedirect('some_url')

        else:
            return render(request, 'auction/register.html', {'form': form})

    else:
        form = RegisterTherapist()

    return render(request, 'auction/register.html', {'form': form})

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
        return render(request, 'auction/login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, ("Logged out"))
    return redirect('index')