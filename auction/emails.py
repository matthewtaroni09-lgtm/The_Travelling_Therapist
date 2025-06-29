from The_Travelling_Therapist.settings import ACTIVE_LINK


email_header = """<section style="font-size: 16px; margin-bottom: 4rem;">
</section>"""

email_footer = """<footer>
  <img src="https://travelingtherapist.ca/media/images/TTT_LOGO.png" alt="Traveling Therapist Logo">
  <br>
  <a href="travelingtherapist.ca">Click to visit The Traveling Therapist Website</a>
  <p style="font-size: 10px; color: #848585;">You are receiving this email because you have registered to use The Traveling Therapist website services. Please do not reply to this email. If you wish to contact us then email The Traveling Therapist at info@travelingtherapist.ca. To ensure you continue to receive these emails, add this email address to your email safelist. Your details will not be disclosed or used by third parties for marketing or promotional purposes.</p>
</footer>"""

def clinic_reserve_not_met(clinic_name, start_date, end_date, payment_type):
    message = email_header
    reserve_type = ''
    if str(payment_type) == 'Flat Fee':
        reserve_type = 'reserve price'
    elif str(payment_type) == 'Fee Split':
        reserve_type = 'reserve split'
    else:
        reserve_type = 'reserve price'
    message = message + """<section style="font-size: 16px; margin-bottom: 4rem;">
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
    message = message + """<section style="font-size: 16px; margin-bottom: 4rem;">
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
    message = message + """<section style="font-size: 16px; margin-bottom: 4rem;">
  <p>Hello <span class="text-weight-bold">""" + clinic_name + """</span>,</p>
  
  <p>It looks like you've created an account; welcome to The Traveling Therapist.</p>
  <p>Below are some quick access links for using The Traveling Therapist service:</p>

  <ol>
    <li><a href="https://travelingtherapist.ca">Login</a>: login, create an auction, and view the progress of your existing auctions once on the site.</li>
    <li><a href="https://travelingtherapist.ca/about">FAQ</a>: interested in trying our service? See how it all works and answers to the most common questions we receive from therapists and clinics, here.</li>
    <li>Questions for us? Feel free to reach out to us here info@travelingtherapist.ca, and we will get back to you as soon as possible.</li>
  </ol>
   
  <p>Thanks for using The Traveling Therapist.</p>
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>

</section>"""
    message = message + email_footer
    return message

def clinic_auction_end(clinic_name, start_date, end_date):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 4rem;">
  <p>Hello <span class="text-weight-bold">""" + clinic_name + """</span>,</p>
  
  <p>You auction has ended and you will be matched with the lowest bidding therapist soon. Look for an email from us shortly to connect you.</p>

  <p>From this point, it is your responsibility to finalize the following outside of The Traveling Therapist with your temporary therapist:</p>
  <ul>
    <li>How they will be paid (cheque, transfer, etc.)</li>
    <li>What you need from them before starting. This could be a copy of their insurance, etc.</li>
    <li>Any site/clinic orientation required on day 1 or in advance of the work term.</li>
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
    message = message + """<section style="font-size: 16px; margin-bottom: 4rem;">
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
    message = message + """<section style="font-size: 16px; margin-bottom: 4rem;">
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
    message = message + """<section style="font-size: 16px; margin-bottom: 4rem;">
  <p>Hello <span class="text-weight-bold">""" + first_name + """ """ + last_name + """</span>,</p>
  
  <p>An auction you were bidding on has ended. </p>
  <p>Unfortunately, you were not the lowest bidder, so another therapist was matched with the clinic.</p>

  <p>Better luck on your next auction.</p>

  <h3>Auction Details:</h3>
  <p>Clinic Name: """ + str(clinic_name) + """</p>
  <p>Therapist Start Date: """ + str(start_date) + """</p>
  <p>Therapist End Date: """ + str(end_date) + """</p>
  
  <p>Thanks for using our service,</p>
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>

</section>"""
    message = message + email_footer
    return message

def therapist_auction_end_win(first_name, last_name, clinic_name, start_date, end_date):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 4rem;">
        <p>Hello <span class="text-weight-bold">""" + first_name + """ """ + last_name + """</span>,</p>
        
        <p>You were the lowest bidder at the end of an auction using The Traveling Therapist. Congratulations!</p>
        <p>Look for an email from us shortly to match you with the clinic. From that point it is your responsibility to contact the clinic and arrange some of the details of your job like how you will be paid (cheque, deposit, etc.)</p>

        <h3>Auction Details:</h3>
        <p>Clinic Name: """ + str(clinic_name) + """</p>
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
    message = message + """<section style="font-size: 16px; margin-bottom: 4rem;">
  <p>Hello <span class="text-weight-bold">""" + first_name + """ """ + last_name + """</span>,</p>
  
  <p>You were bidding on an auction using The Traveling Therapist.</p>
  <p>This auction ended with a """ + str(reserve_type) +  """  which wasn't met. This means that there was no therapist willing to do this temporary job for a """ + str(reserve_type) +  """ low enough for the clinic.</p>
  <p>This auction may be reposted in the near future - stay tuned!</p>
  <p>Not sure what the reserve price is? Check out our FAQ page <a href="https://travelingtherapist.ca/about">here</a>.</p>

  <h3>Auction Details:</h3>
  <p>Clinic Name: """ + str(clinic_name) + """</p>
  <p>Therapist Start Date: """ + str(start_date) + """</p>
  <p>Therapist End Date: """ + str(end_date) + """</p>
  
  <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>

</section>
"""
    message = message + email_footer
    return message

def therapist_welcome(first_name, last_name):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 4rem;">
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
    message = message + """<section style="font-size: 16px; margin-bottom: 4rem;">
        <h1>A New Auction has been created</h1>
        Clinic Name: """ + clinicName + """<br>
        Clinic Location: """ + city + """, """ + province + """<br>
        Clinic email: """ + email + """<br>
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
    message = message + """<section style="font-size: 16px; margin-bottom: 4rem;">
  <p>Dear <span class="text-weight-bold">""" + first_name + """ """ + last_name + """</span>,</p>
  
  This is an email to let you know that a <a href=""" + link + """> new listing you can bid on </a> with the following details has been posted!
  <br><br>
  <b>Placement Term:</b> """ + start_date + """ - """ + end_date + """
  <br>
  <b>Clinic Name:</b> """ + clinic_name + """
  <br>
  <b>Clinic Location:</b> """ + clinic_location + """
  <br><br>
  The clock is ticking, so if you'd like to take the opening, bid away!
  <br>
  There is currently <b>""" + time_remaining + """</b> left in the auction.
  <br><br>
  This auction is a """ + payment_type + """, so remember that """ + payment_type_message + """
  <br><br>
  Remember that The Traveling Therapist is always free to bid for clinicians and at the end of the auction that the clinic is matched with the LOWEST bidder.

    <p>Happy Bidding!</p>
    <br>
    <p style="font-weight: 700; padding-top: 0rem; margin-top: 0; line-height: 0;">The Traveling Therapist Team</p>

</section>"""
    message = message + email_footer
    return message