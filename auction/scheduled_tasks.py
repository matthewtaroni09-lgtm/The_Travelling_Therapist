from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from .models import Account, Auction, Bid, User, Account, AdminSettings
from django.db.models import Min
from . import emails
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

register_events(scheduler)

scheduler.start()

def start(year, month, day, hour, minute, second, id):
    schedule_id = scheduler.add_job(auction_closed, 'cron', year=year, month=month, day=day, hour=hour, minute=minute, second=second, id=id, args=(id,))
    auction = Auction.objects.get(auctionID=id)
    auction.cronID = schedule_id.id
    auction.save()
    scheduler.print_jobs()

def restart(year, month, day, hour, minute, second, id, auction_id):
    scheduler.add_job(auction_closed, 'cron', year=year, month=month, day=day, hour=hour, minute=minute, second=second, id=id, args=(auction_id,))
    auction = Auction.objects.get(auctionID=auction_id)
    auction.cronID = id
    auction.save()
    scheduler.print_jobs()

def print_job():
    scheduler.print_jobs()

def remove_cron_job(id):
    scheduler.remove_job(id)

def auction_closed(id):
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("date and time =", dt_string)
    auction = Auction.objects.get(auctionID=id)
    bids = Bid.objects.filter(auction=id, active=True).annotate(Min('amount')).order_by('amount')
    winningBid = ""
    admin = AdminSettings.objects.all()[:1].get()
    bidding_emails = []
    
    auction.active = False
    auction.closed = True
    print(admin.sendEmails)
    print(bids.count())
    if bids.count() > 0:
        winningBid = bids[0]
        print(winningBid.amount)
        print(winningBid.user.first_name)
        print(winningBid.user.email)
        for bid in bids:
            print('Bid user:' + str(bid.user.email))
            if bid.user.email != winningBid.user.email:
                bidding_emails.append({'email': bid.user.email, 'first_name': bid.user.first_name, 'last_name': bid.user.last_name})
        print(bidding_emails)
        auction.winner = winningBid.user
        auction.winningPrice = winningBid.amount
        auction.save()

        if admin.sendEmails:
            if auction.reservePrice is not None:
                if winningBid.amount > auction.reservePrice:
                    # Therapist email
                    for bid in bids: 
                        send_mail(
                                subject = "Auction Ended - Reserve Not Met",
                                message = "",
                                html_message = emails.therapist_auction_not_met(bid.user.first_name, bid.user.last_name),
                                from_email = settings.EMAIL_HOST_USER,
                                recipient_list = [bid.user.email]
                            )
                    # Clinic email
                    send_mail(
                            subject = "Auction Ended - Reserve Not Met",
                            message = "",
                            html_message = emails.clinic_reserve_not_met(auction.clinic.clinicName),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = [winningBid.user.email]
                        )
            else:
                print('send email')
                # Therapist email
                send_mail(
                        subject = "Auction Ended - You are the Winner2",
                        message = "",
                        html_message = emails.therapist_auction_end_win(winningBid.user.first_name, winningBid.user.last_name, auction.clinic.clinicName, auction.placementStart, auction.placementEnd),
                        from_email = settings.EMAIL_HOST_USER,
                        recipient_list = [winningBid.user.email]
                    )
                # Clinic email
                send_mail(
                        subject = "Auction Ended",
                        message = "",
                        html_message = emails.clinic_auction_end(auction.clinic.clinicName),
                        from_email = settings.EMAIL_HOST_USER,
                        recipient_list = [auction.clinic.user.email]
                    )
                for email in bidding_emails:
                    print(email)
                    send_mail(
                        subject = "Auction Ended - Better Luck Next Time",
                        message = "",
                        html_message = emails.therapist_auction_end_lose(email['first_name'], email['last_name']),
                        from_email = settings.EMAIL_HOST_USER,
                        recipient_list = [email['email']]
                    )   
    else:
        print("no winner")
        auction.save()
        if admin.sendEmails:
            send_mail(
                    subject = "Auction Ended",
                    message = "",
                    html_message = emails.clinic_no_bids(auction.clinic.clinicName),
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list = [auction.clinic.user.email]
                )
    
    return JsonResponse({'data': "success"})