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
    
    
]

if settings.DEBUG: 
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)