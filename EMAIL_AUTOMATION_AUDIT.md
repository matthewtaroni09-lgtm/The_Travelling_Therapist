# Email Automation Audit (Simple)

## Quick Count
- Total send_mail call sites: 33
- Main reusable email templates in code: 17

## Auto Email Types (Plain List)
1. Referral success (user + admin copy)
2. Contact form alert (to info inbox)
3. Listing created (clinic + admin)
4. Registration welcome (clinic/clinician + admin mirrors)
5. Offer submitted confirmation (to clinician)
6. Outbid emails (lowest bidder, other bidders, admin cap warning)
7. Password reset
8. Listing goes live (clinic + admin)
9. New listing blast (to matching clinicians)
10. New listing blast cap warning (admin)
11. Raffle winner (winner + admin)
12. Listing ended - reserve not met
13. Listing ended - winner/loser/no-bid outcomes

## Main Copy Sources
- auction/emails.py
- auction/templates/auction/password/password_reset_email.txt
- auction/templates/auction/password/password_reset_email.html

## Key Wording Issues To Fix
- "lowest offer" appears in several emails
- "reserve" language appears in end-of-listing emails
- Typo: "hHalthcare Facility Name"
- Typo: "ADMIM COPY"
- Typo: "outbit users"

## Suggested Rewrite Order
1. Listing ended + outbid + offer confirmation
2. Listing created/live + welcome emails
3. Referral + raffle
4. Password reset + contact flow
