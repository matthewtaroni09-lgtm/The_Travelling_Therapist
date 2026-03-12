import os
import django

# Set up the Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'The_Travelling_Therapist.settings')
django.setup()

from auction.models import AdminSetting

def create_admin_settings():
    # Try to get the first AdminSetting instance or create a new one
    admin_setting, created = AdminSetting.objects.get_or_create(
        pk=1,
        defaults={
            'sendEmails': True,
            'numAllowedAuctions': 1,
            'defaultAuctionLength': 3600,
            'endAuctionEmailBatchSize': 50  # Defaulting to 50 if not specified
        }
    )

    if not created:
        admin_setting.sendEmails = True
        admin_setting.numAllowedAuctions = 1
        admin_setting.defaultAuctionLength = 3600
        # If we update it, we should keep the existing batch size or set a default if it was null
        if admin_setting.endAuctionEmailBatchSize is None:
             admin_setting.endAuctionEmailBatchSize = 50
        admin_setting.save()
        print("Admin settings updated.")
    else:
        print("Admin settings created.")

if __name__ == "__main__":
    create_admin_settings()
