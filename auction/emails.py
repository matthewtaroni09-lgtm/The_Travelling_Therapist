from datetime import datetime
from django.conf import settings
from The_Travelling_Therapist.settings import ACTIVE_LINK, PROD_LINK

# -----------------------------
# LINK & ASSET RESOLUTION
# -----------------------------

def _get_public_email_base_link():
    """
    Ensures email links resolution points to production host if ACTIVE_LINK
    is set to localhost or 127.0.0.1 during local development.
    """
    base_link = str(ACTIVE_LINK or '').strip()
    lowered = base_link.lower()

    if (
        base_link == ''
        or '127.0.0.1' in lowered
        or 'localhost' in lowered
        or lowered.startswith('http://0.0.0.0')
    ):
        return str(PROD_LINK or '').strip()

    return base_link


EMAIL_BASE_LINK = _get_public_email_base_link()
LOGO_URL_WB = f"{EMAIL_BASE_LINK}/media/images/TTT_LOGO_white_BG.png"

current_year = datetime.now().year

# -----------------------------
# LAYOUT TEMPLATES
# -----------------------------

email_header = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Traveling Therapist</title>
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<style>
  body {{
    margin: 0; padding: 0;
    font-family: Arial, sans-serif;
    background-color: #B2FBDD;
    color: #1B1B1B;
  }}
  .container {{
    max-width: 600px;
    margin: 40px auto;
    background-color: #ffffff;
    border-radius: 8px;
    overflow: hidden;
    padding: 0;
  }}
  .header {{
    background-color: #ffffff;
    text-align: center;
    padding: 20px;
    border-style: solid;
    border-radius: 8px;
  }}
  .header img {{
    max-width: 200px;
    height: auto;
    background-color: #ffffff;
    padding: 5px;
    border-radius: 4px;
    display: block;
    margin: 0 auto;
  }}
  .content {{
    padding: 30px;
    font-size: 16px;
    line-height: 1.6;
    color: #1B1B1B;
  }}
  .content a {{
    color: #02CA90;
    text-decoration: none;
  }}
  .footer {{
    background-color: #1B1B1B;
    color: #aaaaaa;
    font-size: 12px;
    text-align: center;
    padding: 20px;
  }}
  .footer a {{
    color: #9cd2f8;
    text-decoration: none;
  }}
  b {{
    font-weight: 700;
  }}
</style>
</head>
<body style="background-color:#B2FBDD; margin:0; padding:0;">
  <div class="container">
    <div class="header">
      <img src="{LOGO_URL_WB}" alt="The Traveling Therapist Logo" style="padding:5px; border-radius:4px;">
    </div>
"""

email_footer = f"""
    <div class="footer" style="background-color:#1B1B1B; color:#aaaaaa; text-align:center; padding:20px; font-size:12px;">
      &copy; {current_year} The Traveling Therapist. All rights reserved.
    </div>
  </div>
</body>
</html>
"""

# -----------------------------
# ACCOUNT CREATION
# -----------------------------

def clinic_welcome(clinic_name):
    # Setup matching urls from navigation.html
    create_listing_url = f"{EMAIL_BASE_LINK}/create-auction"
    pricing_url = f"{EMAIL_BASE_LINK}/pricing"
    login_url = f"{EMAIL_BASE_LINK}/login"
    profile_url = f"{EMAIL_BASE_LINK}/profile"
    healthcare_facility_guide_url = f"{EMAIL_BASE_LINK}/healthcare-facility-guide"
    
    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{clinic_name}</span>,</p>
  
  <p>Welcome to The Traveling Therapist — we’re excited to support your hiring needs.</p>
  <p>Your account is now active. Here’s everything you need to get started:</p>

  <ul style="padding-left: 20px; line-height: 1.8;">
    <li><a href="{create_listing_url}"><b>Create Listing</b></a>: Create a new listing and start receiving offers from qualified clinicians.</li>
    <li><a href="{create_listing_url}"><b>Review & Accept Offers</b></a>: Review offers submitted on your listing and choose the clinician who best fits your needs — no offers?, no charge to you! Learn more <a href="https://www.youtube.com/watch?v=5V2ec58lGi8">here</a>.</p>
    <li><a href="{profile_url}"><b>Manage Listings</b></a>: Manage your listings, review offers, and track hiring progress.</li>
    <li><a href="{healthcare_facility_guide_url}"><b>Hiring Guides & Resources</b></a>: Explore our new healthcare hiring guides to learn best practices and optimize your recruitment process.</li>
  </ul>

  <p>We're here to help. Contact us anytime by replying to this email.</p>

  <div style="text-align: center; margin: 25px 0;">
    <a href="{create_listing_url}" style="background-color: #02CA90; color: #ffffff; padding: 12px 24px; font-weight: bold; text-decoration: none; border-radius: 5px; display: inline-block;">Post a Job Listing</a>
  </div>

  <p>Thank You for Joining us at The Traveling Therapist</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message


def therapist_welcome(first_name, last_name):
    # Setup matching urls from navigation.html
    login_url = f"{EMAIL_BASE_LINK}/login"
    profile_url = f"{EMAIL_BASE_LINK}/profile"
    index_url = f"{EMAIL_BASE_LINK}/"
    hiring_healthcare_worker_url = f"{EMAIL_BASE_LINK}/hiring_healthcare_worker"
    
    full_name = f"{first_name or ''} {last_name or ''}".strip() or "Clinician"

    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{full_name}</span>,</p>
  
  <p>It looks like you've created an account; welcome to The Traveling Therapist.</p>
  <p>Your account is ready to use. Here’s how to get started:</p>
  
  <ul style="padding-left: 20px; line-height: 1.8;">
    <li><a href="{index_url}"><b>Browse Job Listings & Make Offers</b></a>: View open positions posted by healthcare facilities across Canada. We recently updated our system to let you submit any offer you choose — no restrictions. Facilities can review your skills (<a href="{profile_url}">update your profile</a>), hourly or fee split offers, and select the best fit for their clinic. We never take a cut of your rate, so the offer you make is the rate you’d receive if the clinic selects you!</li>
    <li><a href="{profile_url}"><b>Manage Profile</b></a>: Manage your profile, track your offers, and update your availability.</li>
    <li><a href="{hiring_healthcare_worker_url}"><b>Hiring Guides & Resources</b></a>: Check out our new “Getting Hired with The Traveling Therapist” guide and other resources designed to help you stand out.</li>
  </ul>

  <div style="text-align: center; margin: 25px 0;">
    <a href="{index_url}" style="background-color: #02CA90; color: #ffffff; padding: 12px 24px; font-weight: bold; text-decoration: none; border-radius: 5px; display: inline-block;">Browse Job Listings & Make Offers</a>
  </div>

  <p>Reach out anytime at <a href="mailto:info@travelingtherapist.ca">info@travelingtherapist.ca</a>.</p>
  <p>Thanks for using The Traveling Therapist.</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message

# -----------------------------
# LISTING CREATION
# -----------------------------

def clinic_auction_created(clinic_name):
    how_it_works_url = f"{EMAIL_BASE_LINK}/how_it_works"
    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{clinic_name}</span>,</p>
  
  <p>Thank you for creating a listing on our site! This listing is currently pending.
  We will review the details of your listing and connect with you to collect payment information before your listing can be live on our site. 
  Full details on this can be found on our <a href="{how_it_works_url}">How It Works page</a>.</p>

  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">Thanks for being part of The Traveling Therapist family.</p>
</section>""" + email_footer
    return message


def clinic_auction_live(clinic_name):
    how_it_works_url = f"{EMAIL_BASE_LINK}/how_it_works"
    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{clinic_name}</span>,</p>
  
  <p>Thank you for creating a healthcare job listing on The Traveling Therapist.</p>

  <p>We have moved your listing from pending to LIVE as we have reviewed the contents and collected your payment information. Clinicians may now place offers on your listing for the next 14 days, and you can accept an offer anytime during this window.</p>

  <p>If you have questions, please have a look at our <a href="{how_it_works_url}">How It Works page</a>, or reach out to us by replying to this email with your questions.</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">Thanks for being part of The Traveling Therapist family.</p>
</section>""" + email_footer
    return message


def new_auction_email_to_all(first_name, last_name, link, start_date, end_date, payment_type, clinic_name, clinic_location, time_remaining, auctionID=None):
    full_name = f"{first_name or ''} {last_name or ''}".strip() or "Clinician"
    listing_url = link or (f"{EMAIL_BASE_LINK}/auction/{auctionID}" if auctionID else f"{EMAIL_BASE_LINK}/")
    payment_type_message = ""

    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Dear <span style="font-weight: bold;">{full_name}</span>,</p>
  
  <p>This is an email to let you know that a <a href="{listing_url}">new listing you can place an offer on</a> with the following details has been posted!</p>

  <div style="background-color: #f8f9fa; border-left: 4px solid #02CA90; padding: 15px; margin: 15px 0; border-radius: 4px;">
    <p style="margin: 4px 0;"><b>Placement Term:</b> {start_date} - {end_date}</p>
    <p style="margin: 4px 0;"><b>Healthcare Facility Name:</b> {clinic_name}</p>
    <p style="margin: 4px 0;"><b>Healthcare Facility Location:</b> {clinic_location}</p>
  </div>

  <p>The clock is ticking, so if you'd like to take the opening, place your offer!</p>
  <p>There is currently <b>{time_remaining}</b> left in the listing.</p>
  <p>Remember that The Traveling Therapist is always free to place offers for clinicians and at the end of the listing that the healthcare facility can choose any candidate.</p>

  <div style="text-align: center; margin: 25px 0;">
    <a href="{listing_url}" style="background-color: #02CA90; color: #ffffff; padding: 12px 24px; font-weight: bold; text-decoration: none; border-radius: 5px; display: inline-block;">Learn more about the listing & make an offer</a>
  </div>

  <p>Happy Offering!</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message

# -----------------------------
# OFFERS
# -----------------------------

def therapist_auction_thank_you_bid(first_name, last_name, clinic_name, start_date, auctionID):
    full_name = f"{first_name or ''} {last_name or ''}".strip() or "Clinician"
    listing_url = f"{EMAIL_BASE_LINK}/auction/{auctionID}"
    formatted_date = start_date.strftime("%Y-%m-%d") if hasattr(start_date, 'strftime') else str(start_date)

    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{full_name}</span>,</p>
  
  <p>Thank you for submitting your offer for <a href="{listing_url}"><b>{clinic_name}'s: {formatted_date}</b></a> listing. We appreciate your participation.</p>

  <p>If another candidate submits another offer, you will receive an email.</p>
  <p>You are always welcome to submit another offer for this listing <a href="{listing_url}">here</a>.</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message


def clinician_placed_offer_other_users(first_name, last_name, clinic_name, start_date, auctionID):
    full_name = f"{first_name or ''} {last_name or ''}".strip() or "Clinician"
    listing_url = f"{EMAIL_BASE_LINK}/auction/{auctionID}"
    formatted_date = start_date.strftime("%Y-%m-%d") if hasattr(start_date, 'strftime') else str(start_date)

    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{full_name}</span>,</p>
  
  <p>There's been an update on a listing you previously placed an offer on: <a href="{listing_url}"><b>{clinic_name}'s: {formatted_date}</b></a>.</p>
  <p>Another clinician has placed an offer. This may affect your competitiveness if you're interested in this opportunity. You may submit a new offer at any time before the listing closes.</p>

  <div style="text-align: center; margin: 25px 0;">
    <a href="{listing_url}" style="background-color: #02CA90; color: #ffffff; padding: 12px 24px; font-weight: bold; text-decoration: none; border-radius: 5px; display: inline-block;">Click here to view the listing and place your next offer.</a>
  </div>

  <p>Thank you for participating in the listing. We wish you the best of luck!</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message

# -----------------------------
# CLINIC SELECTS A CLINICIAN
# -----------------------------

def offer_accepted(clinic_name, start_date, end_date):
    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{clinic_name}</span>,</p>
  
  <p>Thank you for choosing a candidate with The Traveling Therapist. Look for an email from us shortly to connect you.</p>

  <p>From this point, it is your responsibility to finalize the following outside of The Traveling Therapist with your clinician:</p>
  <ul style="padding-left: 20px; line-height: 1.8;">
    <li>How they will be paid (cheque, transfer, etc.)</li>
    <li>What you need from them before starting. This could be a copy of their insurance, etc.</li>
    <li>Any site/healthcare facilities orientation required on day 1 or in advance of the work term.</li>
  </ul>

  <h3>Listing Details:</h3>
  <p><b>Therapist Start Date:</b> {start_date}</p>
  <p><b>Therapist End Date:</b> {end_date}</p>

  <p>Thanks for using our service - we hope to see you again soon,</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message


def therapist_auction_end_win(first_name, last_name, clinic_name, start_date, end_date):
    full_name = f"{first_name or ''} {last_name or ''}".strip() or "Clinician"

    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{full_name}</span>,</p>
  
  <p><b>Congratulations!</b> Your offer was selected by <span style="font-weight: bold;">{clinic_name}</span>.</p>
  <p>Look for an email from us shortly to connect you with the clinic. From that point it is your responsibility to contact the healthcare facility and finalize details of your job.</p>

  <h3>Listing Details:</h3>
  <p><b>Healthcare Facility Name:</b> {clinic_name}</p>
  <p><b>Therapist Start Date:</b> {start_date}</p>
  <p><b>Therapist End Date:</b> {end_date}</p>
  
  <p>Thank you and we look forward to having you use our service again soon,</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message


def therapist_auction_end_lose(first_name, last_name, clinic_name, start_date, end_date):
    full_name = f"{first_name or ''} {last_name or ''}".strip() or "Clinician"
    browse_url = f"{EMAIL_BASE_LINK}/"

    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{full_name}</span>,</p>
  
  <p>A listing you were offering on has ended.</p>
  <p>Unfortunately, your offer was not selected by the facility.</p>
  <p>Stay tuned in case that offer falls through.</p>

  <div style="text-align: center; margin: 25px 0;">
    <a href="{browse_url}" style="background-color: #02CA90; color: #ffffff; padding: 12px 24px; font-weight: bold; text-decoration: none; border-radius: 5px; display: inline-block;">Browse more listings & find my next opportunity Here</a>
  </div>

  <h3>Listing Details:</h3>
  <p><b>Healthcare facility Name:</b> {clinic_name}</p>
  <p><b>Therapist Start Date:</b> {start_date}</p>
  <p><b>Therapist End Date:</b> {end_date}</p>
  
  <p>Thanks for being a part of The Traveling Therapist family.</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message

# -----------------------------
# LISTING ENDS WITHOUT MATCH OR EXPIRES
# -----------------------------

def clinic_no_bids(clinic_name, start_date=None, end_date=None):
    repost_url = f"{EMAIL_BASE_LINK}/create-auction"
    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{clinic_name}</span>,</p>
  
  <p>Your listing has now closed and no clinicians submitted an offer this time.</p>

  <p>Don't worry, this happens from time to time. The good news is that listings with no offers are always free to repost.</p>

  <div style="text-align: center; margin: 25px 0;">
    <a href="{repost_url}" style="background-color: #02CA90; color: #ffffff; padding: 12px 24px; font-weight: bold; text-decoration: none; border-radius: 5px; display: inline-block;">Repost My Listing</a>
  </div>

  <p><b>Want to improve your chances of receiving offers? Before reposting, consider:</b></p>
  <ul style="padding-left: 20px; line-height: 1.8;">
    <li>Including a suggested payment amount or hourly compensation on your listing</li>
    <li>Add details about your facility, schedule, include your website and/or video about the opportunity, and patient demographics</li>
    <li>Updating skills, negotiable perks, and payment information</li>
  </ul>

  <p>Thank you for choosing The Traveling Therapist. We look forward to helping you find the right clinician.</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message

def clinic_auction_closed_waiting_email(clinic_name, auctionID):
    listing_url = f"{EMAIL_BASE_LINK}/auction/{auctionID}"
    pricing_url = f"{EMAIL_BASE_LINK}/pricing"

    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{clinic_name}</span>,</p>

  <p>Your listing has reached its 14-day duration and is now marked as <strong>Closed</strong>.</p>

  <p><strong>Action Required:</strong> You currently have pending offers. You have exactly <strong>7 days</strong> to review and select a candidate.
  If no candidate is selected by the end of this period, we will assume you have decided to select no clinician from the set of offers.</p>

  <p>Friendly reminder that your invoice total will be generated based on the candidate you select or decide not to select. Learn more at our <a href="{pricing_url}">Pricing Page</a></p> 

  <div style="text-align: center; margin: 25px 0;">
    <a href="{listing_url}" style="background-color: #02CA90; color: #ffffff; padding: 12px 24px; font-weight: bold; text-decoration: none; border-radius: 5px; display: inline-block;">Review Offers Now</a>
  </div>

  <p>Thank you for using The Traveling Therapist.</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message


def clinic_manual_no_offer_accepted(clinic_name, start_date, end_date, auctionID=None):
    repost_url = f"{EMAIL_BASE_LINK}/create-auction"
    listing_button_html = ""
    if auctionID:
        listing_url = f"{EMAIL_BASE_LINK}/auction/{auctionID}"
        listing_button_html = f'<a href="{listing_url}" style="background-color: #02CA90; color: #ffffff; padding: 12px 24px; font-weight: bold; text-decoration: none; border-radius: 5px; display: inline-block;">View Listing</a>'

    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{clinic_name}</span>,</p>

  <p>You have chosen to select none of the candidate offers available for your listing.</p>
  {listing_button_html}

  <p>Because your listing successfully generated offers from clinicians on our platform, a $50 invoice will be sent to you shortly.</p>
  <p>We're sorry you didn't find the perfect fit this time! We encourage you to create a new listing and consider adjusting the terms or rate to attract the candidate you need.</p>

  <div style="text-align: center; margin: 25px 0;">
    <a href="{repost_url}" style="background-color: #02CA90; color: #ffffff; padding: 12px 24px; font-weight: bold; text-decoration: none; border-radius: 5px; display: inline-block;">Post a New Listing</a>
  </div>

  <h3>Listing Details:</h3>
  <p><b>Therapist Start Date:</b> {start_date}</p>
  <p><b>Therapist End Date:</b> {end_date}</p>

  <p>Thank you for using The Traveling Therapist.</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message

def clinic_automatic_closeout_no_offer(clinic_name, start_date, end_date):
    repost_url = f"{EMAIL_BASE_LINK}/create-auction"
    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{clinic_name}</span>,</p>
  
  <p>Your listing's 7-day review period has expired, and none of the offers from the candidates were selected. As a result, your listing has automatically closed.</p>
  
  <p>Because your listing successfully generated offers from our clinicians, a $50 invoice will be sent to you shortly.</p>
  
  <div style="text-align: center; margin: 25px 0;">
    <a href="{repost_url}" style="background-color: #02CA90; color: #ffffff; padding: 12px 24px; font-weight: bold; text-decoration: none; border-radius: 5px; display: inline-block;">Post a New Listing</a>
  </div>
  
  <h3>Listing Details:</h3>
  <p><b>Therapist Start Date:</b> {start_date}</p>
  <p><b>Therapist End Date:</b> {end_date}</p>
  
  <p>Thank you for using The Traveling Therapist.</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message

# -----------------------------
# REFERRALS & RAFFLES
# -----------------------------

def referral_success_email(referrer_name, new_facility_name, ticket_amount, account_url):
    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>A new user joined using your referral link. Your Tickets are now ready for use in your profile.</p>

  <p>Hi <span style="font-weight: bold;">{referrer_name}</span>,</p>

  <p>Great news — <span style="font-weight: bold;">{new_facility_name}</span> just signed up using your referral link. As a thank-you, here’s <b>{ticket_amount} tickets</b> for you to spend in our raffles! Thanks for helping grow our network. View your referrals: <a href="{account_url}">here</a>.</p>

  <p>Thanks again for helping grow our community. More facilities and clinicians on our platform means faster matches and better coverage for everyone.</p>

  <p>Warm regards,</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message


def raffle_winner_email(first_name, raffle_title, raffle_month, ticket_balance):
    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hi <span style="font-weight: bold;">{first_name}</span>,</p>
  
  <p><b>Great News — you’ve been selected as the winner of the latest Traveling Therapist Raffle!</b></p>

  <p>Your entry was randomly chosen from all eligible submissions, and we’re excited to award you the following prize:</p>

  <p><b>Prize:</b> {raffle_title}</p>
  <p><b>Raffle Date:</b> {raffle_month}</p>

  <p>Your prize will be delivered to you via email from <a href="mailto:info@travelingtherapist.com">info@travelingtherapist.com</a> within the next few days.</p>

  <p>Your current ticket balance is <b>{ticket_balance}</b> tickets.</p>

  <p>Thanks for being an engaged member of The Traveling Therapist community — and enjoy your prize!</p>

  <p>Warmly,</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message

# -----------------------------
# AUTHENTICATION & CONTACT
# -----------------------------

def password_reset(first_name, reset_link):
    name = first_name or "User"
    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{name}</span>,</p>
  
  <p>We received a request to reset your password for your Traveling Therapist account.</p>

  <p>Click the button below to reset your password. If you did not request this, you can safely ignore this email.</p>

  <div style="text-align: center; margin: 25px 0;">
    <a href="{reset_link}" style="background-color: #02CA90; color: #ffffff; padding: 12px 24px; font-weight: bold; text-decoration: none; border-radius: 5px; display: inline-block;">Reset Password</a>
  </div>

  <p>Warm regards,</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message


def contact_us_confirmation(user_name, user_message):
    faq_url = f"{EMAIL_BASE_LINK}/faq"
    register_url = f"{EMAIL_BASE_LINK}/register"

    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span style="font-weight: bold;">{user_name if user_name else 'there'}</span>,</p>
  
  <p>Thank you for contacting us. A representative from The Traveling Therapist will be in touch soon. In the meantime, please feel free to explore our 
  site, <a href="{register_url}">create an account</a>, and read our <a href="{faq_url}">FAQ page</a>.</p>

  <p><b>Copy of your submitted message:</b></p>
  <blockquote style="background-color: #f4f4f4; border-left: 4px solid #02CA90; padding: 12px; margin: 15px 0; border-radius: 4px;">
    {user_message}
  </blockquote>

  <p>Warm regards,</p>
  <br>
  <p style="font-weight: 700; margin-top: 0; line-height: 1.2;">— The Traveling Therapist Team</p>
</section>""" + email_footer
    return message


def auction_created_admin(clinicName, city, province, email, paymentTypes, flatFeeType, auctionStart, auctionEnd, placementStart, placementEnd, auctionID):
    admin_link = f"{EMAIL_BASE_LINK}/admin/auction/auction/{auctionID}/change/"
    message = email_header + f"""<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
        <h1>A New Listing has been created</h1>
        <p><b>Healthcare Facilities Name:</b> {clinicName}</p>
        <p><b>Healthcare Facilities Location:</b> {city}, {province}</p>
        <p><b>Healthcare Facilities email:</b> {email}</p>
        <p><b>Payment Types:</b> {paymentTypes}</p>
        <p><b>Flat Fee Type:</b> {flatFeeType or 'N/A'}</p>
        <p><b>Listing Start:</b> {auctionStart}</p>
        <p><b>Listing End:</b> {auctionEnd}</p>
        <p><b>Placement Start:</b> {placementStart}</p>
        <p><b>Placement End:</b> {placementEnd}</p>
        <p><a href="{admin_link}">Link to listing page</a></p>
    </section>""" + email_footer
    return message