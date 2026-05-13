from django.utils import timezone
from django.contrib import messages
from .models import Account

class WeeklyTicketRewardMiddleware:
    """
    Middleware to award 1 ticket per calendar week to authenticated users 
    when they visit the site, regardless of whether they just logged in 
    or had a persistent session.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # We check for the account and the last award date
                account = request.user.account
                today = timezone.now().date()
                
                # Check if we need to award a ticket (new week or never awarded)
                if not account.last_ticket_award_date or \
                   account.last_ticket_award_date.isocalendar()[1] != today.isocalendar()[1] or \
                   account.last_ticket_award_date.year != today.year:
                    
                    # Update account via ledger
                    account.add_tickets(1, "Weekly visit reward")
                    account.last_ticket_award_date = today
                    account.save()
                    
                    # Store a flag in the session to show the message on the next available page
                    request.session['show_weekly_ticket_message'] = True
                    print(f"Middleware: Awarded 1 ticket to {request.user.username}. Session flag set.")
                    
            except Account.DoesNotExist:
                pass
            except Exception as e:
                print(f"Middleware Error in WeeklyTicketReward: {e}")

        response = self.get_response(request)

        # If the flag is set in the session, add the message now
        if request.user.is_authenticated and request.session.get('show_weekly_ticket_message'):
            messages.success(request, "You've earned 1 ticket for your weekly visit!", extra_tags='ticket_earned')
            del request.session['show_weekly_ticket_message']
            print(f"Middleware: Message injected for {request.user.username}.")

        return response

class ReferralMiddleware:
    """
    Middleware to capture the referral code from the URL (e.g., ?ref=ABC123XYZ)
    and store it in the session for later attribution during signup.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ref_code = request.GET.get('ref')
        if ref_code:
            request.session['referral_code'] = ref_code
            print(f"ReferralMiddleware: Captured ref code {ref_code}")
            
        response = self.get_response(request)
        return response
