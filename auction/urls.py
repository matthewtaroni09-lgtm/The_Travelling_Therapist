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

    # AJAX Calls
    path('auction/data/auction/<auction_id>', views.get_auction_end, name="get-auction-end"),
    path('auction/data/clinic/<clinic_id>', views.get_demogrpahics, name="get-demogrpahics"),
    path("auction/data/all_auctions", views.get_all_auctions, name="get-all-auctions"), 
    path("auction/data/active_auctions_clinic", views.get_active_auctions_clinic, name="get-active-auctions-clinic"), 
    path("auction/data/view_auction_data", views.get_view_auction_data, name="get-active-view-auction-data"), 
    
    path("password_reset", views.password_reset_request, name="password_reset"),
    path("password", PasswordsChangeView.as_view(template_name="auction/registration/change_password.html"), name="change-password")

]

if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)