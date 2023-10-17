from re import template
from django.urls import path
from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import PasswordsChangeView


urlpatterns = [
    # Page Links
    path('', views.AuctionListView.as_view(), name="index"),
    path("about", views.about, name="about"),
    path("profile", views.profile, name="profile"),
    path("create_auction", views.create_auction, name="create-auction"),
    path("register", views.register, name="register"),
    path("login", views.login_user, name="login"),
    path('logout_user', views.logout_user, name="logout"),
    path('auction/<auction_id>', views.view_auction, name="auction"),
    path("contact_us", views.contact, name="contact-us"),
    path("cookie_policy", views.cookie_policy, name="cookie-policy"),
    path("view_all_auctions", views.view_all_auctions, name="view-all-auctions"),
    path("auction_search", views.auction_search, name="auction-search"),
    path("view_user_auctions", views.view_user_auctions, name="view-user-auctions"),
    path("terms_and_conditions", views.terms_and_conditions, name="terms-and-conditions"),
    path("privacy_policy", views.privacy_policy, name="privacy-policy"),
    path("admin_summary", views.admin_summary, name="admin-summary"),

    # AJAX Calls
    path('auction/data/auction/<auction_id>', views.get_auction_end, name="get-auction-end"),
    path('auction/data/clinic/<clinic_id>', views.get_demographics, name="get-demogrpahics"),
    path("auction/data/all_auctions", views.get_all_auctions, name="get-all-auctions"), 
    path("auction/data/active_auctions_clinic", views.get_active_auctions_clinic, name="get-active-auctions-clinic"), 
    path("auction/data/view_auction_data", views.get_view_auction_data, name="get-active-view-auction-data"), 
    path("auction/data/get_practice_types", views.get_practice_types, name="get-practice-types"), 
    path("auction/data/check_provinces", views.check_provinces, name="check-provinces"), 
    path("auction/data/get_popups", views.get_popups, name="get-popups"), 
    path("auction/data/set_acknowledgement", views.set_acknowledgement, name="set-acknowledgement"), 
    path("auction/data/check_user_payment_type", views.check_user_payment_type, name="check-user-payment-type"), 
    
    path("password_reset", views.password_reset_request, name="password_reset"),
    path("password", PasswordsChangeView.as_view(template_name="auction/registration/change_password.html"), name="change-password")
]

if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)