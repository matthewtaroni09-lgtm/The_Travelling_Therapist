from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from .models import Account, Auction, Bid, User, Account, AdminSetting
from django.db.models import Min
from . import emails
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
import logging
logger = logging.getLogger(__name__)

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
    print('!!!!!AUCTION END!!!!!')
    logger.warning('!!!!AUCTION END!!!!')
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("date and time =", dt_string)
    auction = Auction.objects.get(auctionID=id)
    logger.warning(auction.auctionID)
    bids = Bid.objects.filter(auction=id, active=True).annotate(Min('amount')).order_by('amount')
    winningBid = ""
    admin = AdminSetting.objects.all()[:1].get()
    bidding_emails = []
    
    auction.active = False
    auction.closed = True
    logger.warning(admin.sendEmails)
    logger.warning(bids.count())
    if bids.count() > 0:
        winningBid = bids[0]
        logger.warning("Winning Bid: " + str(winningBid.amount))
        logger.warning("Frist Name: " + str(winningBid.user.first_name))
        logger.warning("Winning Email: " + str(winningBid.user.email))
        if auction.reservePrice is not None:
            if winningBid.amount < auction.reservePrice and auction.reservePrice > 0:
                for bid in bids:
                    logger.warning('Bid user:' + str(bid.user.email))
                    if bid.user.email != winningBid.user.email and not any(email_list['email'] == bid.user.email for email_list in bidding_emails):
                        bidding_emails.append({'email': bid.user.email, 'first_name': bid.user.first_name, 'last_name': bid.user.last_name})
                        logger.warning(bidding_emails)
                logger.warning(bidding_emails)
                auction.winner = winningBid.user
                auction.winningPrice = winningBid.amount
            else:
                for bid in bids:
                    logger.warning('Bid user:' + str(bid.user.email))
                    if bid.user.email != winningBid.user.email and not any(email_list['email'] == bid.user.email for email_list in bidding_emails):
                        bidding_emails.append({'email': bid.user.email, 'first_name': bid.user.first_name, 'last_name': bid.user.last_name})
                        logger.warning(bidding_emails)
                logger.warning(bidding_emails)
                auction.winner = winningBid.user
                auction.winningPrice = winningBid.amount
        auction.save()

        if admin.sendEmails:
            if auction.reservePrice is not None:
                if winningBid.amount > auction.reservePrice and auction.reservePrice > 0:
                    # Therapist email
                    for bid in bids:
                        logger.warning("In bids loop")
                        send_mail(
                                subject = "Auction Ended - Reserve Not Met",
                                message = "",
                                html_message = emails.therapist_auction_not_met(bid.user.first_name, bid.user.last_name, auction.clinic.clinicName, auction.placementStart, auction.placementEnd, auction.paymentType),
                                from_email = settings.EMAIL_HOST_USER,
                                recipient_list = [bid.user.email]
                            )
                        send_mail(
                                subject = "Auction Ended - Reserve Not Met",
                                message = "",
                                html_message = "**ADMIN COPY**" + emails.therapist_auction_not_met(bid.user.first_name, bid.user.last_name, auction.clinic.clinicName, auction.placementStart, auction.placementEnd, auction.paymentType),
                                from_email = settings.EMAIL_HOST_USER,
                                recipient_list = ['info@travelingtherapist.ca']
                            )
                    # Clinic email
                    send_mail(
                            subject = "Auction Ended - Reserve Not Met",
                            message = "",
                            html_message = emails.clinic_reserve_not_met(auction.clinic.clinicName, auction.placementStart, auction.placementEnd, auction.paymentType),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = [auction.clinic.user.email]
                        )
                    send_mail(
                            subject = "Auction Ended - Reserve Not Met",
                            message = "",
                            html_message = "**ADMIN COPY**" + emails.clinic_reserve_not_met(auction.clinic.clinicName, auction.placementStart, auction.placementEnd, auction.paymentType),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = ['info@travelingtherapist.ca']
                        )
            else:
                print('send email')
                # Therapist email
                send_mail(
                        subject = "Auction Ended - You are the Winner",
                        message = "",
                        html_message = emails.therapist_auction_end_win(winningBid.user.first_name, winningBid.user.last_name, auction.clinic.clinicName, auction.placementStart, auction.placementEnd),
                        from_email = settings.EMAIL_HOST_USER,
                        recipient_list = [winningBid.user.email]
                    )
                send_mail(
                        subject = "Auction Ended - You are the Winner",
                        message = "",
                        html_message = "**ADMIN COPY**" + emails.therapist_auction_end_win(winningBid.user.first_name, winningBid.user.last_name, auction.clinic.clinicName, auction.placementStart, auction.placementEnd),
                        from_email = settings.EMAIL_HOST_USER,
                        recipient_list = ['info@travelingtherapist.ca']
                    )
                
                # Clinic email
                send_mail(
                        subject = "Auction Ended",
                        message = "",
                        html_message = emails.clinic_auction_end(auction.clinic.clinicName, auction.placementStart, auction.placementEnd),
                        from_email = settings.EMAIL_HOST_USER,
                        recipient_list = [auction.clinic.user.email]
                    )
                send_mail(
                        subject = "Auction Ended",
                        message = "",
                        html_message = "**ADMIN COPY**" + emails.clinic_auction_end(auction.clinic.clinicName, auction.placementStart, auction.placementEnd),
                        from_email = settings.EMAIL_HOST_USER,
                        recipient_list = ['info@travelingtherapist.ca']
                    )
                for email in bidding_emails:
                    print(email)
                    send_mail(
                        subject = "Auction Ended - Better Luck Next Time",
                        message = "",
                        html_message = emails.therapist_auction_end_lose(email['first_name'], email['last_name'], auction.clinic.clinicName, auction.placementStart, auction.placementEnd),
                        from_email = settings.EMAIL_HOST_USER,
                        recipient_list = [email['email']]
                    )   
                    send_mail(
                        subject = "Auction Ended - Better Luck Next Time",
                        message = "",
                        html_message = "**ADMIN COPY**" + emails.therapist_auction_end_lose(email['first_name'], email['last_name'], auction.clinic.clinicName, auction.placementStart, auction.placementEnd),
                        from_email = settings.EMAIL_HOST_USER,
                        recipient_list = ['info@travelingtherapist.ca']
                    )   
    else:
        print("no winner")
        auction.save()
        if admin.sendEmails:
            send_mail(
                    subject = "Auction Ended",
                    message = "",
                    html_message = emails.clinic_no_bids(auction.clinic.clinicName, auction.placementStart, auction.placementEnd),
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list = [auction.clinic.user.email]
                )
            send_mail(
                    subject = "Auction Ended",
                    message = "",
                    html_message = "**ADMIN COPY**" + emails.clinic_no_bids(auction.clinic.clinicName, auction.placementStart, auction.placementEnd),
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list = ['info@travelingtherapist.ca']
                )
    logger.warning('!!!!END!!!!')
    return JsonResponse({'data': "success"})