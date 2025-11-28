from The_Travelling_Therapist.settings import ACTIVE_LINK

# email_templates.py

# Placeholder logo URL
LOGO_URL = "https://travelingtherapist.ca/media/images/TTT_LOGO.png"

from datetime import datetime

# Get the current date and time
current_date_time = datetime.now()

# Extract the year attribute
current_year = current_date_time.year

# Premium email header
email_header = f"""<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Traveling Therapist</title>

<!-- Tell clients to respect light mode colors -->
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
    background-color: #0AEAA9;
    text-align: center;
    padding: 20px;
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

  /* DARK MODE OVERRIDES (for clients that support prefers-color-scheme) */
  @media (prefers-color-scheme: dark) {{
    body, .container {{
      background-color: #121212 !important;
      color: #e6e6e6 !important;
    }}
    .header {{
      background-color: #0AEAA9 !important;
    }}
    .header img {{
      background-color: #ffffff !important; /* Keeps logo background white */
    }}
    .content a {{
      color: #40f0c2 !important;
    }}
    .footer {{
      background-color: #000000 !important;
      color: #cccccc !important;
    }}
  }}
</style>
</head>
<body style="background-color:#B2FBDD; margin:0; padding:0;">
  <div class="container" style="background-color:#ffffff;">
    <div class="header" style="background-color:#0AEAA9; text-align:center; padding:20px;">
      <img src="{LOGO_URL}" alt="The Traveling Therapist Logo" style="background-color:#FFFFFF; padding:5px; border-radius:4px;">
    </div>
"""


email_footer = """
    <div class="footer" style="background-color:#1B1B1B; color:#aaaaaa; text-align:center; padding:20px; font-size:12px;">
      &copy; """ + str(current_year) + """ The Traveling Therapist. All rights reserved.
    </div>
  </div>
</body>
</html>
"""

# -----------------------------
# EMAIL FUNCTIONS
# -----------------------------

def clinic_reserve_not_met(clinic_name, start_date, end_date, payment_type):
    message = email_header
    reserve_type = ''
    if str(payment_type) == 'Flat Fee':
        reserve_type = 'reserve price'
    elif str(payment_type) == 'Fee Split':
        reserve_type = 'reserve split'
    else:
        reserve_type = 'reserve price'
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span class="text-weight-bold">""" + clinic_name + """</span>,</p>
  
  <p>Your auction has reached an end, and no therapist bid low enough to reach your reserve value. As such there will be no match made at this time.</p>

  <p>Feel free to re-create your auction with no """ + str(reserve_type) + """ or a higher """ + str(payment_type).lower() + """ if you'd like to try to fill this position again. Auctions with no """ + str(reserve_type) + """ generally receive more attention and bids than those with """ + str(reserve_type) + """ set, but of course this decision is entirely yours.</p>

  <p>Re-created auctions will still need to be approved by us like any other auction.</p>

  <h3>Auction Details:</h3>
  <p>Therapist Start Date: """ + str(start_date) + """</p>
  <p>Therapist End Date: """ + str(end_date) + """</p>

  <p>Thanks for using our service - we hope to see you again soon,</p>
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>
</section>"""
    message = message + email_footer
    return message

def clinic_no_bids(clinic_name, start_date, end_date):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span class="text-weight-bold">""" + clinic_name + """</span>,</p>
  
  <p>Your auction has reached an end, and there were no bids made. As such there will be no match made at this time.</p>

  <p>Feel free to re-create your auction if you'd like to try to fill this position again.</p>

  <p>Re-created auctions will still need to be approved by us like any other auction.</p>

   <h3>Auction Details:</h3>
  <p>Therapist Start Date: """ + str(start_date) + """</p>
  <p>Therapist End Date: """ + str(end_date) + """</p>

  <p>Thanks for using our service - we hope to see you again soon,</p>
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>
</section>"""
    message = message + email_footer
    return message

def clinic_welcome(clinic_name):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span class="text-weight-bold">""" + clinic_name + """</span>,</p>
  
  <p>It looks like you've created an account; welcome to The Traveling Therapist.</p>
  <p>Below are some quick access links for using The Traveling Therapist service:</p>

  <ol>
    <li><a href="https://travelingtherapist.ca">Login</a>: login, create an auction, and view the progress of your existing auctions once on the site.</li>
    <li><a href="https://travelingtherapist.ca/about">FAQ</a>: interested in trying our service? See how it all works and answers to the most common questions we receive from therapists and healthcare facilities, here.</li>
    <li>Questions for us? Feel free to reach out to us here info@travelingtherapist.ca, and we will get back to you as soon as possible.</li>
  </ol>
   
  <p>Thanks for using The Traveling Therapist.</p>
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>

</section>"""
    message = message + email_footer
    return message

def clinic_auction_end(clinic_name, start_date, end_date):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span class="text-weight-bold">""" + clinic_name + """</span>,</p>
  
  <p>You auction has ended and you will be matched with the lowest bidding therapist soon. Look for an email from us shortly to connect you.</p>

  <p>From this point, it is your responsibility to finalize the following outside of The Traveling Therapist with your temporary therapist:</p>
  <ul>
    <li>How they will be paid (cheque, transfer, etc.)</li>
    <li>What you need from them before starting. This could be a copy of their insurance, etc.</li>
    <li>Any site/healthcare facilities orientation required on day 1 or in advance of the work term.</li>
  </ul>

   <h3>Auction Details:</h3>
  <p>Therapist Start Date: """ + str(start_date) + """</p>
  <p>Therapist End Date: """ + str(end_date) + """</p>

  <p>Your card on file will be charged by The Traveling Therapist within the next 24h.</p>

  <p>Thanks for using our service - we hope to see you again soon,</p>
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>
</section>"""
    message = message + email_footer
    return message

def clinic_auction_created(clinic_name):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span class="text-weight-bold">""" + clinic_name + """</span>,</p>
  
  <p>Thank you for creating an auction on our site! We will review the details of your auction and connect with you to collect payment information before your ad can be live on our site. Full details on this can be found on our <a href="https://travelingtherapist.ca/about">FAQ page</a>.</p>

  <p>Look for us to reach out in the next 24-48h to get this moving for you.</p>
  <br>
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">Thanks for being part of The Traveling Therapist family.</p>
</section>"""
    message = message + email_footer
    return message

def clinic_auction_live(clinic_name):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span class="text-weight-bold">""" + clinic_name + """</span>,</p>
  
  <p>Thank you for creating an auction for your temporary/contract position on The Traveling Therapist.</p>

  <p>We have moved your auction from pending to LIVE as we have reviewed the contents of your posting and collected your payment information. Therapist users may now bid on your auction for the next 14 days, at which point, you will be matched with the lowest bidder.</p>

  <p>If you have questions, please have a look at our <a href="https://travelingtherapist.ca/about">FAQ page</a>, or reach out to us by replying to this email with your questions.</p>
  <br>
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">Thanks for being part of The Traveling Therapist family.</p>
</section>"""
    message = message + email_footer
    return message

def therapist_auction_end_lose(first_name, last_name, clinic_name, start_date, end_date):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span class="text-weight-bold">""" + first_name + """ """ + last_name + """</span>,</p>
  
  <p>An auction you were bidding on has ended. </p>
  <p>Unfortunately, you were not the lowest bidder, so another therapist was matched with the clinic.</p>

  <p>Better luck on your next auction.</p>

  <h3>Auction Details:</h3>
  <p>Healthcare facility Name: """ + str(clinic_name) + """</p>
  <p>Therapist Start Date: """ + str(start_date) + """</p>
  <p>Therapist End Date: """ + str(end_date) + """</p>
  
  <p>Thanks for using our service,</p>
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>

</section>"""
    message = message + email_footer
    return message

def therapist_auction_end_win(first_name, last_name, clinic_name, start_date, end_date):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
        <p>Hello <span class="text-weight-bold">""" + first_name + """ """ + last_name + """</span>,</p>
        
        <p>You were the lowest bidder at the end of an auction using The Traveling Therapist. Congratulations!</p>
        <p>Look for an email from us shortly to match you with the clinic. From that point it is your responsibility to contact the healthcare facility and arrange some of the details of your job like how you will be paid (cheque, deposit, etc.)</p>

        <h3>Auction Details:</h3>
        <p>Healthcare Facility Name: """ + str(clinic_name) + """</p>
        <p>Therapist Start Date: """ + str(start_date) + """</p>
        <p>Therapist End Date: """ + str(end_date) + """</p>
        
        <p>Thank you and we look forward to having you use our service again soon,</p>
        <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>

        </section>"""
    message = message + email_footer
    return message

def therapist_auction_not_met(first_name, last_name, clinic_name, start_date, end_date, payment_type):
    message = email_header
    reserve_type = ''
    if str(payment_type) == 'Flat Fee':
        reserve_type = 'reserve price'
    elif str(payment_type) == 'Fee Split':
        reserve_type = 'reserve split'
    else:
        reserve_type = 'reserve price'
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span class="text-weight-bold">""" + first_name + """ """ + last_name + """</span>,</p>
  
  <p>You were bidding on an auction using The Traveling Therapist.</p>
  <p>This auction ended with a """ + str(reserve_type) +  """  which wasn't met. This means that there was no therapist willing to do this temporary job for a """ + str(reserve_type) +  """ low enough for the clinic.</p>
  <p>This auction may be reposted in the near future - stay tuned!</p>
  <p>Not sure what the reserve price is? Check out our FAQ page <a href="https://travelingtherapist.ca/about">here</a>.</p>

  <h3>Auction Details:</h3>
  <p>hHalthcare Facility Name: """ + str(clinic_name) + """</p>
  <p>Therapist Start Date: """ + str(start_date) + """</p>
  <p>Therapist End Date: """ + str(end_date) + """</p>
  
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>

</section>
"""
    message = message + email_footer
    return message

def therapist_auction_thank_you_bid(first_name, last_name, clinic_name, start_date, auctionID):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span class="text-weight-bold">""" + first_name + """ """ + last_name + """</span>,</p>
  
  <p>Thank you for submitting your bid for <a href=""" + ACTIVE_LINK + "/auction/" + str(auctionID) + """>""" + clinic_name + """ 's: """ + str(start_date.strftime("%Y-%m-%d")) + """</a> auction. We appreciate your participation.</p>
  <p>If another candidate submits a lower bid, you will receive an email allowing you to resubmit a new bid if you wish to stay in the running. </p>
  <br>
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>

</section>
"""
    message = message + email_footer
    return message

def therapist_auction_outbid_lowest(first_name, last_name, clinic_name, start_date, auctionID):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span class="text-weight-bold">""" + first_name + """ """ + last_name + """</span>,</p>
  
  <p>We wanted to let you know that your bid for <a href=""" + ACTIVE_LINK + "/auction/" + str(auctionID) + """>""" + clinic_name + """ 's: """ + str(start_date.strftime("%Y-%m-%d")) + """</a> job opening has been outbid.</p>
  <p>If you'd like to remain in the running, you may submit a new bid at any time before the auction closes.</p>
  <a href=""" + ACTIVE_LINK + "/auction/" + str(auctionID) + """>Click here to place your new bid!</a>
  <p>If you'd like to remain in the running, you may submit a new bid at any time before the auction closes.</p>
  <p>Thank you for participating in the auction. We wish you the best of luck!</p>
  <br>
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>

</section>
"""
    message = message + email_footer
    return message

def therapist_auction_outbid_all_users(first_name, last_name, clinic_name, start_date, auctionID):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span class="text-weight-bold">""" + first_name + """ """ + last_name + """</span>,</p>  
  <p>There's been an update on an auction you previously bid on: <a href=""" + ACTIVE_LINK + "/auction/" + str(auctionID) + """>""" + clinic_name + """ 's: """ + str(start_date.strftime("%Y-%m-%d")) + """</a>.</p>
  <p>Another clinician has placed a new, lower bid. This may affect your competitiveness if you're still interested in this opportunity. If you'd like to remain in the running, you may submit a new bid at any time before the auction closes.</p>
  👉 <a href=""" + ACTIVE_LINK + "/auction/" + str(auctionID) + """>Click here to view the auction and place your next bid.</a>
  <p>Thank you for participating in the auction. We wish you the best of luck!</p>
  <br>
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>
</section>
"""
    message = message + email_footer
    return message

def therapist_welcome(first_name, last_name):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Hello <span class="text-weight-bold">""" + first_name + """ """ + last_name + """</span>,</p>
  
  <p>It looks like you've created an account; welcome to The Traveling Therapist.</p>
  <p>Below are some quick access links for using The Traveling Therapist service:</p>

  <ol>
    <li><a href="https://travelingtherapist.ca">Login</a>: view temporary therapist listings, bid, and change your profile details here.</li>
    <li><a href="https://travelingtherapist.ca/about">FAQ</a>: interested in trying our service? See how it all works and answers to the most common questions we receive from therapists and clinics, here.</li>
    <li>Questions for us? Feel free to reach out to us here info@travelingtherapist.ca, and we will get back to you as soon as possible.</li>
  </ol>
   
  <p>Thanks for using The Traveling Therapist.</p>
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>

</section>"""
    message = message + email_footer
    return message

def auction_created_admin(clinicName, city, province, email, reservePrice, auctionStart, auctionEnd, placementStart, placementEnd, auctionID):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
        <h1>A New Auction has been created</h1>
        Healthcare Facilities Name: """ + clinicName + """<br>
        Healthcare Facilities Location: """ + city + """, """ + province + """<br>
        Healthcare Facilities email: """ + email + """<br>
        Reserve Bid: """ + reservePrice + """<br>
        Auction Start: """ + auctionStart + """<br>
        Auction End: """ + auctionEnd + """<br>
        Placement Start: """ + placementStart + """<br>
        Placement End: """ + placementEnd + """<br>
        <a href=""" + ACTIVE_LINK + "/admin/auction/auction/" + auctionID + "/change/" + """>Link to auction page</a>
        </section><br><br>"""
    message = message + email_footer
    return message

def new_auction_email_to_all(first_name, last_name, link, start_date, end_date, payment_type, clinic_name, clinic_location, time_remaining):
    payment_type_message = ""
    print("in email")
    print(payment_type)
    if payment_type == "Flat Fee":
      payment_type_message = "<b>the price you're bidding is for the entire as posted, not your desired hourly rate!</b>"
    else:
      payment_type_message = "the fee split you're bidding is the percentage YOU want as a clinician for each patient you see."
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 1rem; padding: 10px;">
  <p>Dear <span class="text-weight-bold">""" + first_name + """ """ + last_name + """</span>,</p>
  
  This is an email to let you know that a <a href=""" + link + """> new listing you can bid on </a> with the following details has been posted!
  <br><br>
  <b>Placement Term:</b> """ + start_date + """ - """ + end_date + """
  <br>
  <b>Healthcare Facility Name:</b> """ + clinic_name + """
  <br>
  <b>Healthcare Facility Location:</b> """ + clinic_location + """
  <br><br>
  The clock is ticking, so if you'd like to take the opening, bid away!
  <br>
  There is currently <b>""" + time_remaining + """</b> left in the auction.
  <br><br>
  This auction is a """ + payment_type + """, so remember that """ + payment_type_message + """
  <br><br>
  Remember that The Traveling Therapist is always free to bid for clinicians and at the end of the auction that the healthcare facility is matched with the LOWEST bidder.

    <p>Happy Bidding!</p>
    <br>
    <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>

</section>"""
    message = message + email_footer
    return message