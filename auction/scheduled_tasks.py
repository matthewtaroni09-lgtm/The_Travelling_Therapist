from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from .models import Account, Auction, Bid, User, Account
from django.db.models import Min

# Global variable
scheduler = BackgroundScheduler()
scheduler.start()
scheduler.shutdown()

def start(year, month, day, hour, minute, id):
    # scheduler.add_job(update_something, 'interval', seconds=3)
    scheduler.add_job(update_something, 'cron', year=year, month=month, day=day, hour=hour, minute=minute, id=id, args=(id,))
    scheduler.print_jobs()

def reschedule_job(year, month, day, hour, minute, id):
    scheduler.reschedule_job(id, trigger='cron', year=year, month=month, day=day, hour=hour, minute=minute)
    scheduler.print_jobs()

def update_something(id):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("date and time =", dt_string)
    auction = Auction.objects.get(auctionID=id)
    bids = Bid.objects.filter(auction=id, active=True).annotate(Min('amount')).order_by('amount')
    winningBid = ""
    print(bids.count())
    if bids.count() > 0:
        winningBid = bids[0]
        print(winningBid.amount)
        print(winningBid.user.first_name)
        print(winningBid.user.email)
        auction.active = False
        auction.closed = True
        auction.winner = winningBid.user
        auction.winningPrice = winningBid.amount
        auction.save()
        send_mail(
                subject = "Auction Ended",
                message = "<h1>Your auction ended at:</h1> " + dt_string + ". The winning bid was: " + str(winningBid.amount) + ".",
                from_email = settings.EMAIL_HOST_USER,
                recipient_list = [winningBid.user.email]
            )
    else:
        print("no winner")
        send_mail(
                subject = "Auction Ended",
                message = "<h1>Your auction ended at:</h1>Your auction ended with no winner.",
                from_email = settings.EMAIL_HOST_USER,
                recipient_list = [auction.clinic.user.email]
            )
    
    return JsonResponse({'data': "success"})