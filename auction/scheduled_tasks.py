from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.db.utils import OperationalError
from django_apscheduler.jobstores import DjangoJobStore, register_events
import logging
import pytz
import random

from .models import Account, Auction, Bid, User, AdminSetting, Raffle, RaffleEntry
from . import emails

logger = logging.getLogger(__name__)

# Initialize scheduler with project timezone
scheduler = BackgroundScheduler(timezone=pytz.timezone(settings.TIME_ZONE))
scheduler.add_jobstore(DjangoJobStore(), "default")
register_events(scheduler)
_raffle_check_registered = False


def _resolve_user_email(user):
    email_value = str(getattr(user, 'email', '') or '').strip()
    if email_value:
        return email_value

    username_value = str(getattr(user, 'username', '') or '').strip()
    if '@' in username_value:
        return username_value

    return ''


def get_default_closed_waiting_period_seconds():
    admin_settings = AdminSetting.objects.first()
    if admin_settings is None:
        return 604800  # 7 days default
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

# -----------------------------
#  RAFFLE DRAW TASK
# -----------------------------

def execute_raffle_draw_task(raffle_id=None):
    """
    Identifies ended raffles and randomly draws a winner based on entered ticket weights.
    Sends winner notification email and admin notification.
    """
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
                raffle = Raffle.objects.select_for_update().get(id=r_id, active=True, winner__isnull=True)
            except Raffle.DoesNotExist:
                logger.info(f"Raffle {r_id} was already processed by another task instance.")
                continue

            logger.warning(f'Processing draw for raffle: {raffle.title} (ID: {raffle.id})')
            entries = RaffleEntry.objects.filter(raffle=raffle).select_related('user')
            
            if not entries.exists():
                logger.warning(f'No entries for raffle: {raffle.title}. Deactivating.')
                raffle.active = False
                raffle.save()
                continue

            users = []
            weights = []
            for entry in entries:
                # Exclude staff/admin accounts from winning
                if entry.user.is_superuser or entry.user.is_staff:
                    continue
                users.append(entry.user)
                weights.append(entry.tickets_added)

            if not users:
                logger.warning(f'No eligible entries for raffle: {raffle.title}. Deactivating.')
                raffle.active = False
                raffle.save()
                continue

            winner = random.choices(users, weights=weights, k=1)[0]
            winning_entry = entries.get(user=winner)

            raffle.winner = winner
            raffle.numWinningTickets = winning_entry.tickets_added
            raffle.active = False
            raffle.save()
            logger.warning(f'Winner selected for {raffle.title}: {winner.username}')

            if admin_setting and admin_setting.sendEmails:
                try:
                    raffle_month = raffle.endDate.strftime('%B %Y')
                    ticket_balance = Account.objects.get(user=winner).numTickets
                    html_message = emails.raffle_winner_email(
                        winner.first_name or winner.username, 
                        raffle.title, 
                        raffle_month, 
                        ticket_balance
                    )
                    
                    send_mail(
                        subject="Congratulations! You've Won the Raffle!",
                        message="",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[winner.email],
                        html_message=html_message
                    )
                    send_mail(
                        subject=f"Raffle Winner Selected: {raffle.title}",
                        message=f"Winner selected for '{raffle.title}': {winner.username} ({winner.email})",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=['info@travelingtherapist.ca'],
                    )
                except Exception as e:
                    logger.error(f"Error sending raffle emails: {e}")


def start_raffle(run_date, raffle_id):
    """
    Schedules a date job to run execute_raffle_draw_task at the specified run_date.
    """
    job_id = f"raffle_{raffle_id}"
    if not _ensure_scheduler_started():
        return

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


def raffle_check_job():
    logger.info("Executing periodic raffle check...")
    execute_raffle_draw_task()

# -----------------------------
# LISTING MANAGEMENT TASKS
# -----------------------------

def start(year, month, day, hour, minute, second, id):
    if not _ensure_scheduler_started():
        return

    schedule_id = scheduler.add_job(
        auction_closed, 'cron', 
        year=year, month=month, day=day, hour=hour, minute=minute, second=second, 
        id=id, args=(id,)
    )
    auction = Auction.objects.get(auctionID=id)
    auction.cronID = schedule_id.id
    auction.save()


def restart(year, month, day, hour, minute, second, id, auction_id):
    if not _ensure_scheduler_started():
        return

    scheduler.add_job(
        auction_closed, 'cron', 
        year=year, month=month, day=day, hour=hour, minute=minute, second=second, 
        id=id, args=(auction_id,)
    )
    auction = Auction.objects.get(auctionID=auction_id)
    auction.cronID = id
    auction.save()


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
    try:
        auction = Auction.objects.get(auctionID=auction_id)
        
        # Check if the listing was actively in the decision phase and they let it timeout
        if auction.waitingCloseout:
            bids = Bid.objects.filter(auction=auction, active=True)
            has_bids = bids.exists()
            has_selected_winner = auction.winner_id is not None
            
            # If there are active bids but NO offer was selected when this 7-day period ran out
            if has_bids and not has_selected_winner:
                admin = AdminSetting.objects.first()
                if admin is None or admin.sendEmails:
                    clinic_email = _resolve_user_email(auction.clinic.user) if (auction.clinic and auction.clinic.user) else None
                    if clinic_email:
                        try:
                            send_mail(
                                subject='No Offer Selected',
                                message='',
                                html_message=emails.clinic_automatic_closeout_no_offer(
                                    str(auction.clinic.clinicName),
                                    auction.placementStart,
                                    auction.placementEnd,
                                ),
                                from_email=settings.EMAIL_HOST_USER,
                                recipient_list=[clinic_email, 'info@travelingtherapist.ca'],
                            )
                        except Exception as exc:
                            logger.error(f"Error sending automatic closeout invoice email to clinic {clinic_email}: {exc}")

        auction.active = False
        auction.waitingCloseout = False
        auction.closed = True
        auction.save()
        logger.info(f"Listing {auction_id} finalized and closed.")
    except Auction.DoesNotExist:
        logger.error(f"Auction {auction_id} not found during finalize_waiting_closeout.")


def auction_closed_waiting(auction_id):
    """
    Transitions listing into waiting closeout status after expiry.
    """
    try:
        auction = Auction.objects.get(auctionID=auction_id)
        auction.active = False
        auction.waitingCloseout = True
        auction.closed = False
        auction.save()
    except Auction.DoesNotExist:
        logger.error(f"Auction {auction_id} not found.")


def auction_closed(id):
    """
    Fires when a listing deadline passes.
    If 0 offers were submitted during the active window, sends clinic_no_bids email.
    """
    logger.warning('!!!!AUCTION END EXPIRED!!!!')
    try:
        auction = Auction.objects.get(auctionID=id)
    except Auction.DoesNotExist:
        logger.error(f"Auction {id} not found in auction_closed.")
        return JsonResponse({'error': 'Auction not found'}, status=404)

    was_active = auction.active
    if not was_active:
        logger.info('Skipping auction_closed transition for non-active listing %s.', auction.auctionID)
        return JsonResponse({'data': 'skipped_non_active'})

    auction.active = False
    bids = Bid.objects.filter(auction=auction, active=True)
    active_bid_count = bids.count()

    if active_bid_count == 0:
        auction.waitingCloseout = False
        auction.closed = True
    else:
        auction.waitingCloseout = True
        auction.closed = False

    auction.save()

    if was_active and active_bid_count == 0:
        admin = AdminSetting.objects.first()
        if admin is None or admin.sendEmails:
            try:
                clinic_email = _resolve_user_email(auction.clinic.user) if (auction.clinic and auction.clinic.user) else None
                if clinic_email:
                    send_mail(
                        subject='Your Listing Closed with No Offers',
                        message='',
                        html_message=emails.clinic_no_bids(
                            str(auction.clinic.clinicName),
                            auction.placementStart,
                            auction.placementEnd,
                        ),
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[clinic_email, 'info@travelingtherapist.ca'],
                    )
            except Exception as exc:
                logger.warning('Clinic no-bids email failed to send for auction %s: %s', auction.auctionID, exc)
                
    elif was_active and active_bid_count > 0:
        admin = AdminSetting.objects.first()
        if admin is None or admin.sendEmails:
            try:
                clinic_email = _resolve_user_email(auction.clinic.user) if (auction.clinic and auction.clinic.user) else None
                if clinic_email:
                    send_mail(
                        subject='Review Offers for Your Listing',
                        message='',
                        html_message=emails.clinic_auction_closed_waiting_email(
                            str(auction.clinic.clinicName),
                            auction.auctionID,
                        ),
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[clinic_email, 'info@travelingtherapist.ca'],
                    )
            except Exception as exc:
                logger.warning('Clinic closed waiting email failed to send for auction %s: %s', auction.auctionID, exc)

    if active_bid_count > 0:
        finalize_run_date = timezone.now() + timedelta(seconds=get_default_closed_waiting_period_seconds())
        schedule_waiting_closeout(auction.auctionID, finalize_run_date)
    else:
        remove_cron_job(f"{auction.auctionID}_waiting_closeout")

    return JsonResponse({'data': "success"})


# -----------------------------
# CANDIDATE SELECTION EVENT
# -----------------------------

def offer_accepted(id, winning_bid_id=None):
    """
    Triggered when a clinic selects a clinician.
    Fires 3 emails together:
    1. offer_accepted (to Clinic)
    2. therapist_auction_end_win (to Selected Clinician)
    3. therapist_auction_end_lose (to Non-selected Clinicians who placed offers)
    """
    logger.warning(f'Candidate selection initiated for auction: {id}')
    try:
        auction = Auction.objects.get(auctionID=id)
    except Auction.DoesNotExist:
        logger.error(f"Auction {id} not found.")
        return JsonResponse({'error': 'Auction not found'}, status=404)

    auction.active = False
    auction.waitingCloseout = True
    auction.closed = False
    auction.save()

    winning_bid = None
    if winning_bid_id:
        try:
            winning_bid = Bid.objects.get(id=winning_bid_id, auction=auction)
        except Bid.DoesNotExist:
            logger.error(f"Bid {winning_bid_id} not found for auction {id}.")

    if not winning_bid:
        winning_bid = getattr(auction, 'selected_bid', None) or Bid.objects.filter(auction=auction, active=True).first()

    admin = AdminSetting.objects.first()
    if admin is None or admin.sendEmails:
        # 1. Send offer_accepted email to clinic
        try:
            clinic_user = auction.clinic.user if auction.clinic else None
            if clinic_user and clinic_user.email:
                send_mail(
                    subject='Candidate Selected for Your Listing',
                    message='',
                    html_message=emails.offer_accepted(
                        str(auction.clinic.clinicName),
                        auction.placementStart,
                        auction.placementEnd,
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[clinic_user.email],
                )
        except Exception as exc:
            logger.error(f"Error sending offer_accepted email to clinic: {exc}")

        if winning_bid:
            winning_user = winning_bid.user
            winning_account = getattr(winning_user, 'account', None)
            w_first = winning_user.first_name or (winning_account.firstName if winning_account else '') or winning_user.username
            w_last = winning_user.last_name or (winning_account.lastName if winning_account else '')

            # 2. Send therapist_auction_end_win email to winning clinician
            try:
                if winning_user.email:
                    send_mail(
                        subject="Congratulations! Your Offer Has Been Accepted!",
                        message='',
                        html_message=emails.therapist_auction_end_win(
                            w_first,
                            w_last,
                            str(auction.clinic.clinicName),
                            auction.placementStart,
                            auction.placementEnd,
                        ),
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[winning_user.email],
                    )
            except Exception as exc:
                logger.error(f"Error sending win email to {winning_user.email}: {exc}")

            # 3. Send therapist_auction_end_lose email to all other bidders
            losing_bids = Bid.objects.filter(auction=auction, active=True).exclude(id=winning_bid.id)
            notified_emails = set()
            for bid in losing_bids:
                losing_user = bid.user
                if losing_user and losing_user.email and losing_user.email not in notified_emails and losing_user.email != winning_user.email:
                    notified_emails.add(losing_user.email)
                    try:
                        l_account = getattr(losing_user, 'account', None)
                        l_first = losing_user.first_name or (l_account.firstName if l_account else '') or losing_user.username
                        l_last = losing_user.last_name or (l_account.lastName if l_account else '')
                        send_mail(
                            subject="Listing Update",
                            message='',
                            html_message=emails.therapist_auction_end_lose(
                                l_first,
                                l_last,
                                str(auction.clinic.clinicName),
                                auction.placementStart,
                                auction.placementEnd,
                            ),
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[losing_user.email],
                        )
                    except Exception as exc:
                        logger.error(f"Error sending lose email to {losing_user.email}: {exc}")

    finalize_run_date = timezone.now() + timedelta(seconds=get_default_closed_waiting_period_seconds())
    schedule_waiting_closeout(auction.auctionID, finalize_run_date)
    return JsonResponse({'data': "success"})

# -----------------------------
# OFFER & LIVE BROADCAST TASKS
# -----------------------------

def notify_clinicians_new_offer(auction_id, new_bid_id):
    """
    Notifies all other clinicians who placed offers on this listing when a new offer is submitted.
    Uses clinician_placed_offer_other_users.
    """
    admin = AdminSetting.objects.first()
    if admin and not admin.sendEmails:
        return

    try:
        auction = Auction.objects.get(auctionID=auction_id)
        new_bid = Bid.objects.get(id=new_bid_id)
    except (Auction.DoesNotExist, Bid.DoesNotExist) as exc:
        logger.error(f"Error in notify_clinicians_new_offer: {exc}")
        return

    other_bids = Bid.objects.filter(auction=auction, active=True).exclude(user=new_bid.user)
    notified_users = set()

    for bid in other_bids:
        user = bid.user
        if user and user.email and user.id not in notified_users:
            notified_users.add(user.id)
            account = getattr(user, 'account', None)
            first_name = user.first_name or (account.firstName if account else '') or user.username
            last_name = user.last_name or (account.lastName if account else '')
            try:
                send_mail(
                    subject=f"New Offer Submitted on Listing: {auction.clinic.clinicName}",
                    message="",
                    html_message=emails.clinician_placed_offer_other_users(
                        first_name,
                        last_name,
                        str(auction.clinic.clinicName),
                        auction.placementStart,
                        auction.auctionID,
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                )
            except Exception as exc:
                logger.error(f"Error sending clinician_placed_offer_other_users email to {user.email}: {exc}")


def notify_all_clinicians_auction_live(auction_id):
    """
    Sends new_auction_email_to_all to all eligible clinicians when an admin approves a listing to LIVE.
    """
    admin = AdminSetting.objects.first()
    if admin and not admin.sendEmails:
        return

    try:
        auction = Auction.objects.get(auctionID=auction_id)
    except Auction.DoesNotExist:
        logger.error(f"Auction {auction_id} not found.")
        return

    if auction.type:
        clinicians = User.objects.filter(account__userType=auction.type, is_active=True)
    else:
        clinicians = User.objects.filter(account__userType__isnull=False, is_active=True).exclude(account__userType__name='Clinic')

    link = f"{emails.EMAIL_BASE_LINK}/auction/{auction.auctionID}"
    start_date_str = auction.placementStart.strftime("%Y-%m-%d") if auction.placementStart else ""
    end_date_str = auction.placementEnd.strftime("%Y-%m-%d") if auction.placementEnd else ""
    clinic_name = str(auction.clinic.clinicName) if auction.clinic else ""
    clinic_location = f"{auction.clinic.city}, {auction.clinic.province}" if auction.clinic else ""
    payment_types = auction.get_payment_types_display() if hasattr(auction, 'get_payment_types_display') else str(getattr(auction, 'paymentTypes', ''))

    now = timezone.now()
    if auction.auctionEnd and auction.auctionEnd > now:
        diff = auction.auctionEnd - now
        time_remaining = f"{diff.days} days"
    else:
        time_remaining = "14 days"

    for user in clinicians:
        recipient_email = _resolve_user_email(user)
        if not recipient_email:
            continue
        account = getattr(user, 'account', None)
        first_name = user.first_name or (account.firstName if account else '') or user.username
        last_name = user.last_name or (account.lastName if account else '')

        try:
            send_mail(
                subject=f"New Job Listing Live: {clinic_name}",
                message="",
                html_message=emails.new_auction_email_to_all(
                    first_name,
                    last_name,
                    link,
                    start_date_str,
                    end_date_str,
                    payment_types,
                    clinic_name,
                    clinic_location,
                    time_remaining,
                    auctionID=auction.auctionID,
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[recipient_email],
            )
        except Exception as exc:
            logger.error(f"Error sending new_auction_email_to_all to {recipient_email}: {exc}")


def remove_cron_job(id):
    if not scheduler.running:
        return
    try:
        scheduler.remove_job(id)
    except Exception:
        logger.info("Cron job %s was not present when removal was requested.", id)


def print_job():
    scheduler.print_jobs()