email_header = """<header>
  <img src="https://travelingtherapist.ca/media/images/TTT_LOGO.png" alt="Traveling Therapist Logo">
</header>

<section style="font-size: 16px; margin-bottom: 4rem;">
</section>"""

email_footer = """<footer>
  <a href="travelingtherapist.ca">Click to visit The Traveling Therapist Website</a>
  <p style="font-size: 10px; color: #848585;">You are receiving this email because you have registered to use The Traveling Therapist website services. Please do not reply to this email. If you wish to contact us then email The Traveling Therapist at info@travelingtherapist.ca. To ensure you continue to receive these emails, add this email address to your email safelist. Your details will not be disclosed or used by third parties for marketing or promotional purposes.</p>
</footer>"""

def therapist_auction_end_win(first_name, last_name):
    message = email_header
    message = message + """<section style="font-size: 16px; margin-bottom: 4rem;">
        <p>Hello <span class="text-weight-bold">""" + first_name + """ """ + last_name + """</span>,</p>
        
        <p>You were the lowest bidder at the end of an auction using The Traveling Therapist. Congratulations!</p>
        <p>Look for an email from us shortly to match you with the clinic. From that point it is your responsibility to contact the clinic and arrange some of the details of your job like how you will be paid (cheque, deposit, etc.)</p>
        
        <p>Thank you and we look forward to having you use our service again soon,</p>
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
        <a href=""" + "http://127.0.0.1:8000/admin/auction/auction/" + auctionID + "/change/" + """>Link to auction page</a>
        </section>"""
    message = message + email_footer
    return message
