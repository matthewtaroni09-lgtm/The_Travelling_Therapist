from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from .models import Account, Auction, Bid, User, Account, AdminSettings
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
    admin = AdminSettings.objects.all()[:1].get()
    print(admin.sendEmails)
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
        if admin.sendEmails:
            print('send email')
            # Therapist email
            send_mail(
                    subject = "Auction Ended",
                    message = "Your auction ended at: " + dt_string + ". The winning bid was: " + str(winningBid.amount) + ".",
                    # html_message = "<h1>Your auction ended at:</h1> " + dt_string + ". The winning bid was: " + str(winningBid.amount) + ".",
                    html_message = """<section style="font-size: 16px; margin-bottom: 4rem;">
                            <p>Hello <span class="text-weight-bold">""" + auction.clinic.user.first_name + """</span>,</p>
                            
                            <p>You were the lowest bidder at the end of an auction using The Traveling Therapist. Congratulations!</p>
                            <p>Look for an email from us shortly to match you with the clinic. From that point it is your responsibility to contact the clinic and arrange some of the details of your job like how you will be paid (cheque, deposit, etc.)</p>
                            
                            <p>Thank you and we look forward to having you use our service again soon,</p>
                            <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>

                            </section>""",
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list = [winningBid.user.email]
                )
            # Clinic email
            send_mail(
                    subject = "Auction Ended",
                    message = "Your auction ended at: " + dt_string + ". The winning bid was: " + str(winningBid.amount) + ".",
                    # html_message = "<h1>Your auction ended at:</h1> " + dt_string + ". The winning bid was: " + str(winningBid.amount) + ".",
                    html_message = """<section style="font-size: 16px; margin-bottom: 4rem;">
                    <p>Hello <span class="text-weight-bold">""" + auction.clinic.clinicName + """</span>,</p>
                    
                    <p>You auction has ended and you will be matched with the lowest bidding therapist soon. Look for an email from us shortly to connect you.</p>

                    <p>From this point, it is your responsibility to finalize the following outside of The Traveling Therapist with your temporary therapist:</p>
                    <ul>
                        <li>How they will be paid (cheque, transfer, etc.)</li>
                        <li>What you need from them before starting. This could be a copy of their insurance, etc.</li>
                        <li>Any site/clinic orientation required on day 1 or in advance of the work term.</li>
                    </ul>

                    <p>Your card on file will be charged by The Traveling Therapist within the next 24h.</p>

                    <p>Thanks for using our service - we hope to see you again soon,</p>
                    <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>
                    </section>""",
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list = [winningBid.user.email]
                )
    else:
        print("no winner")
        if admin.sendEmails:
            send_mail(
                    subject = "Auction Ended",
                    message = "<h1>Your auction ended at:</h1>Your auction ended with no winner.",
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list = [auction.clinic.user.email]
                )
    
    return JsonResponse({'data': "success"})