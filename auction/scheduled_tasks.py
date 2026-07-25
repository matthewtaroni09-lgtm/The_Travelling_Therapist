from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from .models import Account, Auction, Bid, User, Account, AdminSetting
from django.db.models import Min
from . import emails
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.db.utils import OperationalError
import logging
import pytz
import random
from django.utils import timezone

logger = logging.getLogger(__name__)

# Initialize scheduler with the project's timezone
scheduler = BackgroundScheduler(timezone=pytz.timezone(settings.TIME_ZONE))
scheduler.add_jobstore(DjangoJobStore(), "default")
register_events(scheduler)
_raffle_check_registered = False


def get_default_closed_waiting_period_seconds():
    admin_settings = AdminSetting.objects.first()
    if admin_settings is None:
        return 604800
    return admin_settings.defaultClosedWaitingPeriodLength


def _ensure_scheduler_started():
    global _raffle_check_registered

    if scheduler.running:
        return True

    try:
        if not _raffle_check_registered:
            scheduler.add_job(
                raffle_check_job,
                "interval",
                minutes=1,
                id="raffle_check_job",
                replace_existing=True,
            )
            _raffle_check_registered = True
        scheduler.start()
        return True
    except OperationalError as exc:
        logger.warning("Scheduler start skipped because database is unavailable: %s", exc)
        return False

def execute_raffle_draw_task(raffle_id=None):
    """
    Logic to identify ended raffles and pick a winner.
    """
    from auction.models import Raffle, Account, AdminSetting, RaffleEntry
    from django.db import transaction
    now = timezone.now()
    
    if raffle_id:
        active_raffles = Raffle.objects.filter(id=raffle_id, active=True)
    else:
        active_raffles = Raffle.objects.filter(active=True, endDate__lte=now, winner__isnull=True)

    if not active_raffles.exists():
        logger.info(f"No raffles due for draw at {now}")
        return

    admin_setting = AdminSetting.objects.first()
    raffle_ids = list(active_raffles.values_list('id', flat=True))

    for r_id in raffle_ids:
        with transaction.atomic():
            try:
                # Lock the raffle row to prevent concurrent draws from multiple processes
                raffle = Raffle.objects.select_for_update().get(id=r_id, active=True, winner__isnull=True)
            except Raffle.DoesNotExist:
                logger.info(f"Raffle {r_id} was already processed by another task instance.")
                continue

            logger.warning(f'Processing draw for raffle: {raffle.title} (ID: {raffle.id})')
            
            # Get all users who entered THIS specific raffle
            entries = RaffleEntry.objects.filter(raffle=raffle).select_related('user')
            
            if not entries.exists():
                logger.warning(f'No entries for raffle: {raffle.title}. Deactivating.')
                raffle.active = False
                raffle.save()
                continue

            users = []
            weights = []
            for entry in entries:
                # Exclude Admin/Staff from winning (Ghost Tickets)
                if entry.user.is_superuser or entry.user.is_staff:
                    continue
                users.append(entry.user)
                weights.append(entry.tickets_added)

            if not users:
                logger.warning(f'No eligible entries (non-admin) for raffle: {raffle.title}. Deactivating.')
                raffle.active = False
                raffle.save()
                continue

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
                    # Generate HTML email content
                    raffle_month = raffle.endDate.strftime('%B %Y')
                    ticket_balance = Account.objects.get(user=winner).numTickets
                    html_message = emails.raffle_winner_email(
                        winner.first_name or winner.username, 
                        raffle.title, 
                        raffle_month, 
                        ticket_balance
                    )
                    
                    # Plain text fallback
                    text_message = f"Hi {winner.first_name or winner.username},\n\nGreat News — you’ve been selected as the winner of this month’s Traveling Therapist Raffle!\n\nYour entry was randomly chosen from all eligible submissions, and we’re excited to award you the following prize:\n\nPrize: {raffle.title}\nRaffle Month: {raffle_month}\n\nYour prize will be delivered to you via info@travelingtherapist.com within the next few days.\n\nYour current ticket balance is {ticket_balance} tickets.\n\nThanks for being an engaged member of The Traveling Therapist community — and enjoy your prize!\n\nWarmly,\nThe Traveling Therapist Team"

                    send_mail(
                        subject="Congratulations! You've Won the Raffle!",
                        message=text_message,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[winner.email],
                        html_message=html_message
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

    if not _ensure_scheduler_started():
        return

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


def start(year, month, day, hour, minute, second, id):
    if not _ensure_scheduler_started():
        return

    schedule_id = scheduler.add_job(auction_closed, 'cron', year=year, month=month, day=day, hour=hour, minute=minute, second=second, id=id, args=(id,))
    auction = Auction.objects.get(auctionID=id)
    auction.cronID = schedule_id.id
    auction.save()
    scheduler.print_jobs()

def restart(year, month, day, hour, minute, second, id, auction_id):
    if not _ensure_scheduler_started():
        return

    scheduler.add_job(auction_closed, 'cron', year=year, month=month, day=day, hour=hour, minute=minute, second=second, id=id, args=(auction_id,))
    auction = Auction.objects.get(auctionID=auction_id)
    auction.cronID = id
    auction.save()
    scheduler.print_jobs()

def schedule_waiting_closeout(auction_id, run_date):
    if not _ensure_scheduler_started():
        return

    job_id = f"{auction_id}_waiting_closeout"
    if timezone.is_naive(run_date):
        run_date = timezone.make_aware(run_date, pytz.timezone(settings.TIME_ZONE))

    scheduler.add_job(
        finalize_waiting_closeout,
        'date',
        run_date=run_date,
        id=job_id,
        args=(auction_id,),
        replace_existing=True,
    )

def finalize_waiting_closeout(auction_id):
    auction = Auction.objects.get(auctionID=auction_id)
    auction.active = False
    auction.waitingCloseout = False
    auction.closed = True
    auction.save()

def print_job():
    scheduler.print_jobs()

def remove_cron_job(id):
    if not scheduler.running:
        return
    try:
        scheduler.remove_job(id)
    except Exception:
        logger.info("Cron job %s was not present when removal was requested.", id)

def auction_closed(id):
    print('!!!!!AUCTION END!!!!!')
    logger.warning('!!!!AUCTION END!!!!')
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print("date and time =", dt_string)
    auction = Auction.objects.get(auctionID=id)
    logger.warning(auction.auctionID)
    bids = Bid.objects.filter(auction=id, active=True).annotate(Min('amount')).order_by('amount')
    auction.active = False
    auction.waitingCloseout = True
    auction.closed = False
    logger.warning(bids.count())
    auction.save()

    finalize_run_date = auction.auctionEnd + timedelta(seconds=get_default_closed_waiting_period_seconds())
    schedule_waiting_closeout(auction.auctionID, finalize_run_date)
    logger.warning('!!!!END!!!!')
    return JsonResponse({'data': "success"})
