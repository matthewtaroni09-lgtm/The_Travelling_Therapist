# from re import template
from django.urls import path
from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .views import PasswordsChangeView


urlpatterns = [
    # Page Links
    # path('', views.AuctionListView.as_view(), name="index"),
    path('', views.index, name="index"),
    path("about", views.about, name="about"),
    path("profile", views.profile, name="profile"),
    path("account", views.profile),
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
    path("admin_raffle_management", views.admin_raffle_management, name="admin-raffle-management"),
    path("test", views.test, name="test"),
    path("benefits", views.service_benefits_page, name="benefits"),
    path("what_is_TTT", views.what_is_TTT, name="what-is-TTT"),
    path("faq", views.faq, name="faq"),
    path("how_it_works", views.how_it_works, name="how-it-works"),
    path("mission_vision", views.mission_vision, name="mission-vision"),
    path("healthcare_facility_guide", views.healthcare_facility_guide, name="healthcare-facility-guide"),
    path("clinician_guide", views.clinician_guide, name="clinician-guide"),
    path("non_traditional_hiring", views.non_traditional_hiring, name="non-traditional-hiring"),
    path("hospital_guide", views.hospital_guide, name="hospital-guide"),
    path("LTC_guide", views.LTC_guide, name="LTC-guide"),
    path("hiring_healthcare_worker", views.hiring_healthcare_worker, name="hiring-healthcare-worker"),
    path("direct_employer_recruitment", views.direct_employer_recruitment, name="direct-employer-recruitment"),
    path("headhunter_recruitment", views.headhunter_recruitment, name="headhunter_recruitment"),
    path("hiring_with_the_traveling_therapist", views.hiring_with_the_traveling_therapist_view, name="hiring-with-the-traveling-therapist"),
    path("retirement_home_hiring_guide", views.retirement_home_hiring_guide, name="retirement-home-hiring-guide"),
    path("job_boards", views.job_boards, name="job-boards"),
    path("private_clinic_hiring_guide", views.private_clinic_hiring_guide, name="private-clinic-hiring-guide"),
    path("referrals_and_networks", views.referrals_and_networks, name="referrals-and-networks"),
    path("facility-referral", views.referral_program, name="referral-program"),
    path("what_are_raffles", views.what_are_raffles, name="what-are-raffles"),
    path("surveys", views.surveys, name="surveys"),
    path("platform-updates", views.platform_updates_hub, name="platform-updates"),
    path("platform-updates/v8-0", views.update_v8_0, name="update-v8-0"),
    path("platform-updates/v6-1", views.update_v6_1, name="update-v6-1"),
    path("platform-updates/v6-0", views.update_v6_0, name="update-v6-0"),

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
    path("auction/data/join_raffle", views.join_raffle, name="join-raffle"), 
    path("auction/data/admin_raffle_api", views.admin_raffle_api, name="admin-raffle-api"), 
    
    path("password_reset", views.password_reset_request, name="password_reset"),
    path("password", PasswordsChangeView.as_view(template_name="auction/registration/change_password.html"), name="change-password")
]

if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)