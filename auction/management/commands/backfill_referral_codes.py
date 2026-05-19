import string
import random
from django.core.management.base import BaseCommand
from auction.models import Account
    
accounts_missing_code = Account.objects.filter(referral_code__isnull=True) | Account.objects.filter(referral_code='')

count = 0
for account in accounts_missing_code:
    # Generate unique 8-character code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # Ensure it's strictly unique in the DB
    while Account.objects.filter(referral_code=code).exists():
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
    account.referral_code = code
    account.save()
    count += 1

print(f"Successfully generated and assigned unique referral codes for {count} older users.")