from django.urls import path
from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Page Links
    path('', views.index, name="index"),
    path("about", views.about, name="about"),
    path("profile", views.login_user, name="profile"),
    # path("register", views.register, name="register"),
    path("register", views.register_therapist, name="register-therapist"),  # new
    path('create_auction', views.create_auction, name="create-auction"),
    path("login", views.login_user, name="login"),
    path('logout_user', views.logout_user, name="logout"),
    path('auction/<auction_id>', views.view_auction, name="auction"),

    # AJAX Calls
    path('auction/data/auction/<auction_id>', views.get_auction_end, name="get-auction-end"),
    path('auction/data/clinic/<clinic_id>', views.get_demogrpahics, name="get-demogrpahics"),
    # path('auction/create_bid/<auction_id>', views.create_bid, name="create-bid"),
    # path('auction/send_email_message/', views.send_email_message, name="send-email_message"),
    # path("auction/datas/", views.index_info, name="index_info"), 
    
]

if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)