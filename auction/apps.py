from django.apps import AppConfig

class AuctionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auction'
    def ready(self):
        import auction.signals
        
        # Fix for Python 3.12 SMTP starttls issue with Django 4.0.4
        import smtplib
        import sys
        if sys.version_info >= (3, 12):
            original_starttls = smtplib.SMTP.starttls
            def patched_starttls(self, keyfile=None, certfile=None, context=None):
                # Django 4.0 passes keyfile and certfile, which are removed in Python 3.12.
                # In Python 3.12, starttls only takes 'context'.
                if context is None:
                    import ssl
                    context = ssl.create_default_context()
                return original_starttls(self, context=context)
            smtplib.SMTP.starttls = patched_starttls

