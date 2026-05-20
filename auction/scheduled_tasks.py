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
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
import logging
import pytz
import random
from django.utils import timezone

logger = logging.getLogger(__name__)

# Initialize scheduler with the project's timezone
scheduler = BackgroundScheduler(timezone=pytz.timezone(settings.TIME_ZONE))
scheduler.add_jobstore(DjangoJobStore(), "default")
register_events(scheduler)

def execute_raffle_draw_task(raffle_id=None):
    """
    Logic to identify ended raffles and pick a winner.
    """
    from auction.models import Raffle, Account, AdminSetting, RaffleEntry
    now = timezone.now()
    
    if raffle_id:
        active_raffles = Raffle.objects.filter(id=raffle_id, active=True)
    else:
        active_raffles = Raffle.objects.filter(active=True, endDate__lte=now, winner__isnull=True)

    if not active_raffles.exists():
        logger.info(f"No raffles due for draw at {now}")
        return

    admin_setting = AdminSetting.objects.first()

    for raffle in active_raffles:
        logger.warning(f'Processing draw for raffle: {raffle.title} (ID: {raffle.id})')
        
        # Get all users who entered THIS specific raffle
        entries = RaffleEntry.objects.filter(raffle=raffle).select_related('user')
        
        if not entries.exists():
            logger.warning(f'No entries for raffle: {raffle.title}. Deactivating.')
            raffle.active = False
            raffle.save()
            continue

        users = [entry.user for entry in entries]
        weights = [entry.tickets_added for entry in entries]

        # Weighted random choice based on tickets entered
        winner = random.choices(users, weights=weights, k=1)[0]
        
        # Get the entry record to see how many tickets they spent
        winning_entry = entries.get(user=winner)

        raffle.winner = winner
        raffle.numWinningTickets = winning_entry.tickets_added
        raffle.active = False
        raffle.save()
        logger.warning(f'Winner selected for {raffle.title}: {winner.username}')

        if admin_setting and admin_setting.sendEmails:
            try:
                send_mail(
                    subject="Congratulations! You've Won the Raffle!",
                    message=f"Hi {winner.first_name},\n\nGreat News — you’ve been selected as the winner of this month’s Traveling Therapist Raffle!'\n\nYour entry was randomly chosen from all eligible submissions, and we’re excited to award you the following prize:\n\n Prize: {raffle.title}!\n\nRaffle Month: {raffle.endDate.strftime('%B %Y')}\n\nYour prize will be delivered to you via info@travelingtherapist.com within the next few days.\n\nYour current ticket balance is {Account.objects.get(user=winner).numTickets} tickets.\n\nThanks for being an engaged member of The Traveling Therapist coommunity — and enjoy your prize!\n\nWarmly,\nThe Traveling Therapist Team",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[winner.email],
                )
                send_mail(
                    subject=f"Raffle Winner Selected: {raffle.title}",
                    message=f"A winner has been selected for the raffle '{raffle.title}'.\n\nWinner: {winner.username} ({winner.email})\nTickets held: {winning_entry.tickets_added}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=['info@travelingtherapist.ca'],
                )
            except Exception as e:
                logger.error(f"Error sending raffle emails: {e}")

    # Account.objects.update(numTickets=0) - Removed as per user request to keep tickets persistent.

def start_raffle(run_date, raffle_id):
    """
    Schedules a one-time precise draw for a raffle.
    """
    from auction.models import Raffle
    job_id = f"raffle_{raffle_id}"

    # Ensure run_date is aware
    if timezone.is_naive(run_date):
        run_date = timezone.make_aware(run_date, pytz.timezone(settings.TIME_ZONE))

    scheduler.add_job(
        execute_raffle_draw_task, 
        'date', 
        run_date=run_date,
        id=job_id,
        args=[raffle_id],
        replace_existing=True
    )

    raffle = Raffle.objects.get(id=raffle_id)
    raffle.cronID = job_id
    raffle.save()
    logger.warning(f"Scheduled precise draw for raffle '{raffle.title}' at {run_date}")

def raffle_check_job():
    logger.info("Executing periodic raffle check...")
    execute_raffle_draw_task()

# Register the periodic check job directly
scheduler.add_job(
    raffle_check_job,
    "interval",
    minutes=1,
    id="raffle_check_job",
    replace_existing=True
)

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
    admin = AdminSetting.objects.first()
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
