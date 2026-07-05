from auction.models import Account, RaffleTicket
    
# Find all accounts that have 0 tickets
accounts_needing_tickets = Account.objects.filter(numTickets=0)
    
count = 0
for account in accounts_needing_tickets:
     # Check if they already received a signup reward in the ledger to prevent double-dipping
     has_signup_reward = RaffleTicket.objects.filter(user=account.user, reason="Signup reward").exists()
        
     if not has_signup_reward:
            # Give them 5 tickets in the ledger and update their balance
            account.add_tickets(5, "Signup reward (Backfilled)")
            count += 1

print(f"Successfully backfilled 5 tickets for {count} older users.")c