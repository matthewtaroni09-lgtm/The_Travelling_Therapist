from django.apps import AppConfig

class AuctionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auction'
    print('inside auction config')
    def ready(self):
        import auction.signals

