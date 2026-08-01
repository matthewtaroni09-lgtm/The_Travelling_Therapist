from asyncio.format_helpers import _format_args_and_kwargs
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re
from unicodedata import category
import uuid
from wsgiref.simple_server import demo_app
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.generic import ListView, CreateView
from django.utils import timezone

from The_Travelling_Therapist.settings import ACTIVE_LINK

from django.forms import inlineformset_factory
from .forms import RegisterAcount, AuctionForm, BidForm, UserFormClinic, UserFormTherapist, ProfileUpdateClinic, CreateUserForm, PasswordChangingForm, ContactForm, DemographicForm, PracticeAreaForm, AuctionAccountForm, MessageAcknowledgementForm
import pytz
from django.urls import reverse_lazy
import datetime
from datetime import timedelta
from . import scheduled_tasks
from . import emails
from .models import PROVINCES, Account, AdminSetting, Auction, Bid, Demographic, DemographicType, PracticeArea, PracticeAreaType, User, Account, UserType, PopupMessage, MessageAcknowledgement, Page, PaymentType, Number, Raffle, RaffleEntry, Referral, RaffleTicket, LISTING_SKILL_OPTIONS
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models.query_utils import Q
from django.db.models import Min, Sum
import json
import requests
import logging
logger = logging.getLogger(__name__)

DEFAULT_PERK_OPTIONS = [
    'Relocation assistance',
    'Housing/accommodation',
    'Signing bonus',
    'Flexible schedule',
]


def _effective_auction_sort_key(auction):
    return (auction.is_effectively_closed(), auction.auctionEnd or timezone.now())

CLINICIAN_SKILL_OPTIONS_BY_TYPE = {
    'physio': [
        'Canadian Physiotherapy License',
        'PT Resident',
        'Physiotherapy Insurance',
        'First Aid/CPR/AED',
        'Digital/Software Based Charting',
        'AI Charting',
        'Working with a PTA/Rehab Assistant Experience',
        'Outpatient & Community Experience',
        'Hospital/Long Term Care/Retirement Home Experience',
        'Home care Experience',
        'Virtual Care Experience',
        'Orthopedics Experience',
        'Neurological Experience',
        'Cardiorespiratory Experience',
        'Sports Experience',
        "Women's Health & Pelvic Health Experience",
        'Acupuncture',
        'Spinal Manipulation',
        'Pelvic Internal Examination',
        'Wound Care',
        'Tracheal Suctioning',
        'Administering a Substance by Inhalation',
    ],
    'pta': [
        'Diploma/Degree in PTA/OTA/Rehab Assistant',
        'Kinesiology Degree',
        'Kinesiologist Certification',
        'Personal Trainer Certification',
        'Practice Insurance',
        'First Aid/CPR/AED',
        'Digital/Software Based Charting',
        'AI Charting',
        'Working with a PT Experience',
        'Working with an OT Experience',
        'Outpatient & Community Experience',
        'Hospital/Long Term Care/Retirement Home Experience',
        'Home care Experience',
        'Virtual Care Experience',
        'Orthopedics Experience',
        'Neurological Experience',
        'Cardiorespiratory Experience',
        'Geriatrics Experience',
        'Sports Experience',
        "Women's Health & Pelvic Health Experience",
    ],
    'rmt': [
        'Canadian Registered Massage Therapy License',
        'Massage Therapy Insurance',
        'First Aid/CPR/AED',
        'Digital/Software Based Charting',
        'AI Charting',
        'Outpatient & Community Experience',
        'Hospital/Long Term Care/Retirement Home Experience',
        'Home care Experience',
        'Orthopedics Experience',
        'Sports Experience',
        "Women's Health & Pelvic Health Experience",
        'Acupuncture',
    ],
}

DEFAULT_REGULATED_CLINICIAN_SKILL_OPTIONS = [
    'Canadian License to Practice',
    'Practice Insurance',
    'First Aid/CPR/AED',
    'Hospital/Long Term Care/Retirement Home Experience',
    'Homecare Experience',
    'Orthopedics Experience',
    'Geriatrics Experience',
    'Sports Experience',
    "Women's Health & Pelvic Health Experience",
]

DEFAULT_NON_REGULATED_CLINICIAN_SKILL_OPTIONS = [
    'Practice Insurance',
    'First Aid/CPR/AED',
    'Hospital/Long Term Care/Retirement Home Experience',
    'Homecare Experience',
    'Orthopedics Experience',
    'Geriatrics Experience',
    'Sports Experience',
    "Women's Health & Pelvic Health Experience",
]

DEFAULT_REGULATED_CLINICIAN_SKILL_OPTIONS_LOWER = {name.lower() for name in DEFAULT_REGULATED_CLINICIAN_SKILL_OPTIONS}

NON_REGULATED_CLINICIAN_KEYWORDS = [
    'dietary aide',
    'pta/ota/rehab assistant',
    'personal support worker',
    'psw',
    'recreation therapist',
    'dental assistant',
]


def _clean_text(value):
    return str(value or '').strip()


def _resolve_user_email(user):
    email_value = str(getattr(user, 'email', '') or '').strip()
    if email_value:
        return email_value

    username_value = str(getattr(user, 'username', '') or '').strip()
    if '@' in username_value:
        return username_value

    return ''


def resolve_clinician_skill_key(type_label):
    normalized = _clean_text(type_label).lower()
    if 'physio' in normalized or 'physiotherapist' in normalized or 'physiotherapy' in normalized:
        return 'physio'
    if (
        'pta' in normalized
        or 'ota' in normalized
        or 'rehab assistant' in normalized
        or 'rehab assis' in normalized
        or 'rehab ass' in normalized
    ):
        return 'pta'
    if (
        'rmt' in normalized
        or 'massage therapist' in normalized
        or 'registered massage therapist' in normalized
        or 'massage therapy' in normalized
    ):
        return 'rmt'
    return 'default'


def include_license_skill_for_type(type_label):
    normalized = _clean_text(type_label).lower()
    return not any(keyword in normalized for keyword in NON_REGULATED_CLINICIAN_KEYWORDS)


def get_clinician_skill_options_for_type(type_label):
    if not include_license_skill_for_type(type_label):
        return list(DEFAULT_NON_REGULATED_CLINICIAN_SKILL_OPTIONS)

    skill_key = resolve_clinician_skill_key(type_label)
    if skill_key in CLINICIAN_SKILL_OPTIONS_BY_TYPE:
        return list(CLINICIAN_SKILL_OPTIONS_BY_TYPE[skill_key])

    return list(DEFAULT_REGULATED_CLINICIAN_SKILL_OPTIONS)


def suppress_legacy_default_skill_for_type(type_label, skill_name):
    if not include_license_skill_for_type(type_label) and _clean_text(skill_name).lower() == 'canadian license to practice':
        return True

    skill_key = resolve_clinician_skill_key(type_label)
    if skill_key not in ('physio', 'pta', 'rmt'):
        return False
    return _clean_text(skill_name).lower() in DEFAULT_REGULATED_CLINICIAN_SKILL_OPTIONS_LOWER


def get_account_profile_image_urls(account):
    raw_images = []
    for image_field_name in ('imageOne', 'imageTwo', 'imageThree', 'imageFour'):
        image_field_value = getattr(account, image_field_name, None)
        image_name = str(getattr(image_field_value, 'name', image_field_value) or '').strip()
        if not image_name:
            continue
        if image_name.lower() in ('default.jpg', 'images/default.jpg'):
            continue
        raw_images.append(image_name)

    image_urls = []
    for image_name in raw_images:
        image_url = image_name if image_name.startswith('/media/') else f"/media/{image_name}"
        if image_url not in image_urls:
            image_urls.append(image_url)

    if len(image_urls) == 0:
        image_urls = ['/media/images/no-image.jpg']

    return image_urls


def parse_required_skills_payload(raw_payload):
    try:
        payload = json.loads(raw_payload) if raw_payload else []
    except (TypeError, ValueError):
        payload = []

    rows = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        name = _clean_text(item.get('name'))
        if not name:
            continue

        requirement_raw = _clean_text(item.get('requirement')).lower()
        requirement = 'Preferred' if requirement_raw == 'preferred' else 'Required'
        selected = bool(item.get('selected', False))

        rows.append({
            'name': name,
            'selected': selected,
            'requirement': requirement,
            'custom': bool(item.get('custom', False)),
        })
    return rows


def parse_negotiable_perks_payload(raw_payload):
    try:
        payload = json.loads(raw_payload) if raw_payload else []
    except (TypeError, ValueError):
        payload = []

    rows = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        name = _clean_text(item.get('name'))
        if not name:
            continue

        included = bool(item.get('selected', False) or item.get('included', False))
        details = _clean_text(item.get('details'))

        try:
            amount = int(item.get('amount')) if item.get('amount') not in (None, '') else 0
        except (TypeError, ValueError):
            amount = 0

        rows.append({
            'name': name,
            'selected': included,
            'included': included,
            'amount': max(amount, 0),
            'details': details,
            'custom': bool(item.get('custom', False)),
        })
    return rows


def build_clinician_skills_payload(account, skill_options=None):
    if skill_options is None:
        skill_options = get_clinician_skill_options_for_type(str(getattr(account, 'userType', '')))

    selected_names = {name.lower() for name in account.get_clinician_skill_names()}
    payload = []

    for option in skill_options:
        payload.append({
            'name': option,
            'selected': option.lower() in selected_names,
            'custom': False,
        })

    type_label = str(getattr(account, 'userType', '') or '')
    known_lower = {option.lower() for option in skill_options}
    for selected_name in account.get_clinician_skill_names():
        if suppress_legacy_default_skill_for_type(type_label, selected_name):
            continue
        if selected_name.lower() not in known_lower:
            payload.append({
                'name': selected_name,
                'selected': True,
                'custom': True,
            })

    return payload


def parse_clinician_skills_payload(raw_payload):
    try:
        payload = json.loads(raw_payload) if raw_payload else []
    except (TypeError, ValueError):
        payload = []

    rows = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        name = _clean_text(item.get('name'))
        if not name:
            continue

        rows.append({
            'name': name,
            'selected': bool(item.get('selected', False)),
            'custom': bool(item.get('custom', False)),
        })

    return rows


def parse_offer_selected_skills_payload(raw_payload):
    try:
        payload = json.loads(raw_payload) if raw_payload else []
    except (TypeError, ValueError):
        payload = []

    selected = []
    for item in payload:
        if isinstance(item, dict):
            name = _clean_text(item.get('name'))
            is_selected = bool(item.get('selected', False))
            if name and is_selected:
                selected.append(name)
        elif isinstance(item, str):
            name = _clean_text(item)
            if name:
                selected.append(name)

    return list(dict.fromkeys(selected))


def build_skill_match(required_skill_rows, clinician_skill_names):
    clinician_map = {name.lower() for name in clinician_skill_names}
    required_met = []
    required_missing = []
    preferred_met = []
    preferred_missing = []

    for row in required_skill_rows:
        name = _clean_text(row.get('name'))
        if not name:
            continue

        is_match = name.lower() in clinician_map
        requirement = _clean_text(row.get('requirement')) or 'Required'
        if requirement == 'Preferred':
            (preferred_met if is_match else preferred_missing).append(name)
        else:
            (required_met if is_match else required_missing).append(name)

    return {
        'required_met': required_met,
        'required_missing': required_missing,
        'preferred_met': preferred_met,
        'preferred_missing': preferred_missing,
        'required_total': len(required_met) + len(required_missing),
        'preferred_total': len(preferred_met) + len(preferred_missing),
    }

class PasswordsChangeView(PasswordChangeView):
    form_class = PasswordChangingForm
    success_url = reverse_lazy('profile')

def contact(request):
    admin = AdminSetting.objects.first()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
            }
            r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
            result = r.json()

            print(result)
            if result['success'] and result['score'] > .5:
                subject = "Website Inquiry" 
                body = {
                'first_name': form.cleaned_data['first_name'], 
                'last_name': form.cleaned_data['last_name'], 
                'email': form.cleaned_data['email_address'], 
                'message':form.cleaned_data['message'], 
                }
                message = "\n".join(body.values())

                try:
                    if admin.sendEmails:
                        send_mail(subject, message, 'info@travelingtherapist.ca', ['info@travelingtherapist.ca'])
                        # Send confirmation email to the person who contacted us
                        first_name = form.cleaned_data['first_name']
                        user_email = form.cleaned_data['email_address']
                        send_mail(
                            subject="We've received your message — The Traveling Therapist",
                            message=f"Hi {first_name},\n\nThank you for contacting us. A representative will be in touch soon.\n\nYour message:\n{form.cleaned_data['message']}",
                            html_message=emails.contact_us_confirmation(first_name, form.cleaned_data['message']),
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[user_email],
                        )
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                except:
                    HttpResponse('Other email error.')
                return redirect ("index")
            else:
                messages.error(request, 'Invalid reCAPTCHA. Please try again.')
                logger.warning('****CONTACT US PAGE**** Captcha failure')
                return render(request, "auction/contact_us.html", {})
        else:
            return render(request, "auction/contact_us.html", {'form': form})
    else:
        form = ContactForm(None)
        return render(request, "auction/contact_us.html", {'form': form, 'recaptcha_site_key':settings.GOOGLE_RECAPTCHA_SITE_KEY})

def view_all_auctions(request):
    auctions = Auction.objects.filter(Q(active=True) | Q(closed=True) | Q(waitingCloseout=True), deleted=False)
    auctions = sorted(auctions, key=_effective_auction_sort_key)
    print(auctions)
    return render(request, 'auction/partials/auction_list.html', {'auction': auctions, 'length': len(auctions), 'auction_search': True})

def auction_search(request):
    city = request.POST.get('citySelect')
    payment_type_select = request.POST.get('paymentTypeSelect')
    status_select = request.POST.get('statusSelect')
    clinic_input = (request.POST.get('clinicInput') or '').strip()
    search_all_checkbox = request.POST.get('searchAllCheckbox')

    city_fitler = ''
    payment_type_fitler = ''
    status_select_fitler = ''
    clinic_fitler = ''
    type_filter = ''

    # Filter city
    if city == '0':
        city_fitler = Q()
    else:
        city_fitler = Q(clinic__city=city)

    # Filter payment types    
    if payment_type_select == '0':
        payment_type_fitler = Q()
    elif payment_type_select == 'Fee Split':
        payment_type_fitler = Q(paymentTypes__icontains='Fee Split') | Q(paymentType__name='Fee Split')
    elif payment_type_select == 'Flat Fee (Hourly)':
        payment_type_fitler = (Q(paymentTypes__icontains='Flat Fee') | Q(paymentType__name='Flat Fee')) & Q(flatFeeType='hourly')
    elif payment_type_select == 'Flat Fee (Total Contract Price)':
        payment_type_fitler = (Q(paymentTypes__icontains='Flat Fee') | Q(paymentType__name='Flat Fee')) & Q(flatFeeType='total_contract')
    else:
        payment_type_fitler = Q()

    now = timezone.now()

    # Filter statues
    if status_select == '0':
        status_select_fitler = Q()
    else:
        if status_select == 'Active':
            status_select_fitler = Q(active=True, closed=False, auctionEnd__gt=now)
        elif status_select == 'Closed':
            status_select_fitler = Q(closed=True) | Q(waitingCloseout=True) | Q(auctionEnd__lte=now)
        else:
            status_select_fitler = Q()
    # Filter clinic search
    if clinic_input == '':
        clinic_fitler = Q()
    else:
        clinic_fitler = Q(clinic__clinicName__icontains=clinic_input)

    if request.user.is_authenticated and str(request.user.account.userType) != 'Clinic' and search_all_checkbox != 'on' and not request.user.is_staff:
        type_filter = Q(type=request.user.account.userType)
    else:
        type_filter = Q()

    filter = city_fitler & payment_type_fitler & status_select_fitler & clinic_fitler & type_filter
    # filter = city_fitler & payment_type_fitler & status_select_fitler & clinic_fitler
    print(filter)
    auctions_queryset = Auction.objects.filter(filter, deleted=False)
    
    if clinic_input:
        normalized_search = clinic_input.lower()
        
        def sort_by_clinic_match(auction):
            clinic_name = (auction.clinic.clinicName or '').strip().lower()
            if clinic_name == normalized_search:
                match_score = 0
            elif clinic_name.startswith(normalized_search):
                match_score = 1
            else:
                match_score = 2
            return (match_score, _effective_auction_sort_key(auction))

        auctions = sorted(
            auctions_queryset,
            key=sort_by_clinic_match,
        )
    else:
        auctions = sorted(auctions_queryset, key=_effective_auction_sort_key)
    return render(request, 'auction/partials/auction_list.html', {'auction': auctions, 'length': len(auctions), 'auction_search': True})

def index(request):
    logger.warning('Homepage was accessed at '+str(datetime.datetime.now())+' hours!')
    auction = ''
    now = timezone.now()
    if request.user.is_authenticated == False or str(request.user.account.userType) == 'Clinic' or request.user.is_staff:
        auctions = Auction.objects.filter((Q(active=True) | Q(closed=True) | Q(waitingCloseout=True)) & Q(deleted=False))
    elif request.user.is_authenticated == True and request.user.account.userType != 'Clinic':
        auctions = Auction.objects.filter((Q(active=True) | Q(closed=True) | Q(waitingCloseout=True)) & Q(type=request.user.account.userType) & Q(deleted=False))
    auctions = sorted(auctions, key=_effective_auction_sort_key)
    cities = []
    payment_type_options = []
    statuses = []
    for auction in auctions:
        if auction.clinic.city not in cities:
            cities.append(auction.clinic.city)
        for payment_type in auction.get_payment_type_filter_labels():
            if payment_type not in payment_type_options:
                payment_type_options.append(payment_type)
        
        status = ''
        if auction.is_effectively_active():
            status = 'Active'
        elif auction.is_effectively_closed():
            status = 'Closed'
        if status not in statuses:
            statuses.append(status)

    ordered_payment_type_options = []
    for payment_type in ['Fee Split', 'Flat Fee (Hourly)', 'Flat Fee (Total Contract Price)']:
        if payment_type in payment_type_options:
            ordered_payment_type_options.append(payment_type)

    context = {
        'auctions': auctions,
        'cities': cities,
        'payment_types': ordered_payment_type_options,
        'statuses': statuses,
        'auction_search': False,
        'path': 'home'
    }
    return render(request, 'auction/index.html', context)

def terms_and_conditions(request):
    return render(request, 'auction/terms_and_conditions.html', {})

def privacy_policy(request):
    return render(request, 'auction/privacy_policy.html', {})

def test(request):
    return render(request, 'auction/test2.html', {})

def view_user_auctions(request):
    auctions = ''
    user_type = request.user.account.userType
    auctions = Auction.objects.filter(Q(active=True) | Q(closed=True) | Q(waitingCloseout=True), type=user_type, deleted=False)
    auctions = sorted(auctions, key=_effective_auction_sort_key)
    return render(request, 'auction/partials/auction_list.html', {'auction': auctions})

# Page Links
def about(request):
    return render(request, 'auction/about.html', {'path': 'about'})

def faq(request):
    return render(request, 'auction/faq.html', {'path': 'faq'})

def pricing(request):
    return render(request, 'auction/pricing.html', {'path': 'pricing'})

def how_it_works(request):
    return render(request, 'auction/how_it_works.html', {'path': 'how-it-works'})

def facility_how_to(request):
    return render(request, 'auction/facility-how-to.html', {'path': 'facility-how-to'})

def mission_vision(request):
    return render(request, 'auction/mission_vision.html', {'path': 'mission-vision'})

def cookie_policy(request):
    return render(request, 'auction/cookie_policy.html', {})

def healthcare_facility_guide(request):
    return render(request, 'auction/healthcare_facility_guide.html', {'path': 'healthcare-facility-guide'})

def clinician_guide(request):
    return render(request, 'auction/clinician_guide.html', {'path': 'clinician-guide'})

def casual_work(request):
    return render(request, 'auction/casual_work.html', {'path': 'casual-work'})

def maternity(request):
    return render(request, 'auction/maternity.html', {'path': 'maternity'})

def non_traditional_hiring(request):
    return render(request, 'auction/non_traditional_hiring.html', {'path': 'non-traditional-hiring'})

def hospital_guide(request):
    return render(request, 'auction/hospital_guide.html', {'path': 'hospital-guide'})

def LTC_guide(request):
    return render(request, 'auction/LTC_guide.html', {'path': 'LTC-guide'})

def hiring_healthcare_worker(request):
    return render(request, 'auction/hiring_healthcare_worker.html', {'path': 'hiring-healthcare-worker'})

def direct_employer_recruitment(request):
    return render(request, 'auction/direct_employer_recruitment.html', {'path': 'direct-employer-recruitment'})

def headhunter_recruitment(request):
    return render(request, 'auction/headhunter_recruitment.html', {'path': 'headhunter_recruitment'})

def hiring_with_the_traveling_therapist_view(request):
    return render(request, 'auction/hiring_with_the_traveling_therapist.html', {'path': 'hiring-with-the-traveling-therapist'})

def sort_by_auction_end(listing):
    return listing.auctionEnd or timezone.now()

def profile(request):
    if request.user.is_authenticated == False:
        return render(request, 'auction/profile.html', {})
    parameter = {}
    show_form = False
    user = request.user
    account = user.account
    profile_images = get_account_profile_image_urls(account)
    parameter.update({
        'profile_images': profile_images,
        'profile_image_count': len(profile_images),
    })
    
    # Trigger referral verification check
    account.check_and_award_referral()
    
    # Raffle and Referral data
    tickets = account.numTickets  # Sync'd by add_tickets or can use total_tickets property
    joined_raffles = RaffleEntry.objects.filter(user=user).select_related('raffle')
    
    referral_link = account.get_referral_link()
    successful_referrals = account.get_successful_referrals_count()
    ticket_history = RaffleTicket.objects.filter(user=user).order_by('-created_at')

    # Next weekly award date (7-day rolling cooldown)
    now = timezone.now()
    last_award = account.last_ticket_award_date
    if not last_award or (now.date() - last_award).days >= 7:
        parameter['next_award_date'] = now.isoformat() # Available now
    else:
        next_award = last_award + timedelta(days=7)
        # Combine with start of day for a consistent countdown
        next_award_dt = datetime.datetime.combine(next_award, datetime.time.min)
        # Use pytz to ensure the datetime is aware of the project's local timezone
        local_tz = pytz.timezone(settings.TIME_ZONE)
        next_award_dt = local_tz.localize(next_award_dt)
        parameter['next_award_date'] = next_award_dt.isoformat()
    
    # Clinic Profile
    if str(request.user.account.userType).split(' ')[-1] == "Clinic":
        active_raffles = Raffle.objects.filter(active=True, target_audience__in=['Both', 'Clinic'])
        print(request.method)
        # Not closed and not deleted counts any auctions that are active or have no status selected
        now = timezone.now()
        active_auctions_list = Auction.objects.filter(active=True, waitingCloseout=False, closed=False, deleted=False, clinic=request.user.account, auctionEnd__gt=now)
        past_auctions_list = Auction.objects.filter(deleted=False, clinic=request.user.account).filter(Q(closed=True) | Q(waitingCloseout=True) | Q(auctionEnd__lte=now)).order_by('-auctionEnd')
        pending_auctions_list = Auction.objects.filter(active=False, waitingCloseout=False, closed=False, deleted=False, clinic=request.user.account)
        num_pending = pending_auctions_list.count()
        submitted_profile = False
        submitted_auction = False

        if request.method == 'POST':   # This Will Be Run When I Submit My Form. And Possibly Pass New Data.
            user_clinic_form = UserFormClinic(request.POST, instance=request.user)  # request.POST To Pass The POST Data
            profile_clinic_form = ProfileUpdateClinic(request.POST, request.FILES, instance=request.user.account)  # File Data (images) Users Try To Upload.
            print(user_clinic_form.is_valid())
            print(profile_clinic_form.is_valid())
            if user_clinic_form.is_valid() and profile_clinic_form.is_valid():
                user_form = user_clinic_form.save(commit=False)
                user_form.username = user_clinic_form.cleaned_data.get('email')
                user_form.save()
                profile_instance = profile_clinic_form.save(commit=False)
                if request.POST.get('imageOne-clear') == 'on':
                    profile_instance.imageOne = 'default.jpg'
                profile_instance.save()
                # messages.success(request, f'Your profile has been updated!')
                return HttpResponseRedirect('/profile#profile')
            else:
                print("fail")
                parameter.update({
                    'active_auctions_list': active_auctions_list,
                    'past_auctions_list': past_auctions_list,
                    'pending_auctions_list': pending_auctions_list,
                    'num_pending': num_pending,
                    'user_clinic_form': user_clinic_form,
                    'profile_clinic_form': profile_clinic_form,
                    'submitted_profile': submitted_profile,
                    'submitted_auction': submitted_auction,
                    'show_form': show_form,
                    'user': user,
                    'tickets': tickets,
                    'joined_raffles': joined_raffles,
                    'active_raffles': active_raffles,
                    'referral_link': referral_link,
                    'successful_referrals': successful_referrals,
                    'ticket_history': ticket_history,
                    'next_award_date': parameter.get('next_award_date')
                })
                return render(request, 'auction/profile.html', parameter)
        else:
            user_clinic_form = UserFormClinic(instance=request.user)
            profile_clinic_form = ProfileUpdateClinic(instance=request.user.account)
            if 'submitted' in request.GET:
                submitted_profile = True
            parameter.update({
                    'active_auctions_list': active_auctions_list,
                    'past_auctions_list': past_auctions_list,
                    'pending_auctions_list': pending_auctions_list,
                    'num_pending': num_pending,
                    'user_clinic_form': user_clinic_form,
                    'profile_clinic_form': profile_clinic_form,
                    'submitted_profile': submitted_profile,
                    'submitted_auction': submitted_auction,
                    'show_form': show_form,
                    'user': user,
                    'tickets': tickets,
                    'joined_raffles': joined_raffles,
                    'active_raffles': active_raffles,
                    'referral_link': referral_link,
                    'successful_referrals': successful_referrals,
                    'ticket_history': ticket_history,
                    'next_award_date': parameter.get('next_award_date')
                })
            return render(request, 'auction/profile.html', parameter)
    # Therapist Profile
    else:
        active_raffles = Raffle.objects.filter(active=True, target_audience__in=['Both', 'Clinician'])
        print(request.method)
        therapist_type = request.user.account.userType
        therapist_bids = Bid.objects.filter(
            user=request.user,
            auction__type=therapist_type,
            auction__deleted=False,
        )
        therapist_auctions = list(Auction.objects.filter(
            auctionID__in=therapist_bids.values_list('auction_id', flat=True),
            deleted=False,
        ).distinct())
        active_auctions_list = sorted(
            [listing for listing in therapist_auctions if listing.is_effectively_active()],
            key=sort_by_auction_end,
            reverse=True,
        )
        past_auctions_list = sorted(
            [listing for listing in therapist_auctions if listing.is_effectively_closed()],
            key=sort_by_auction_end,
            reverse=True,
        )
        therapist_offer_history = list(
            Bid.objects.filter(user=user).select_related('auction', 'auction__clinic').order_by('-created')
        )
        therapist_offer_history_by_auction = {}
        for bid in therapist_offer_history:
            therapist_offer_history_by_auction.setdefault(bid.auction_id, []).append(bid)

        for auction in active_auctions_list + past_auctions_list:
            auction.therapist_offer_history = therapist_offer_history_by_auction.get(auction.auctionID, [])
        therapist_type_label = str(request.user.account.userType or '')
        therapist_skill_options = get_clinician_skill_options_for_type(therapist_type_label)
        clinician_skills_payload = build_clinician_skills_payload(request.user.account, therapist_skill_options)
        selected_profile_skill_names = request.user.account.get_clinician_skill_names()
        skill_option_names = {name.lower() for name in therapist_skill_options}
        custom_profile_skills = [
            name for name in selected_profile_skill_names
            if name.lower() not in skill_option_names and not suppress_legacy_default_skill_for_type(therapist_type_label, name)
        ]
        if request.method == 'POST':
            user_therapist_form = UserFormTherapist(request.POST, instance=request.user)
            if user_therapist_form.is_valid():
                user_form = user_therapist_form.save(commit=False)
                user_form.username = user_therapist_form.cleaned_data.get('email')
                user_form.save()

                clinician_skills = parse_clinician_skills_payload(request.POST.get('clinicianSkillsPayload', '[]'))
                request.user.account.clinicianSkills = clinician_skills
                request.user.account.save(update_fields=['clinicianSkills'])

                # messages.success(request, f'Your profile has been updated!')
                return HttpResponseRedirect('/profile#profile-t')
            else:
                parameter.update({
                    'active_auctions_list': active_auctions_list,
                    'past_auctions_list': past_auctions_list,
                    'user_therapist_form': user_therapist_form,
                    'user': user,
                    'tickets': tickets,
                    'joined_raffles': joined_raffles,
                    'active_raffles': active_raffles,
                    'referral_link': referral_link,
                    'successful_referrals': successful_referrals,
                    'ticket_history': ticket_history,
                    'next_award_date': parameter.get('next_award_date'),
                    'therapist_offer_history': therapist_offer_history,
                    'skill_options': therapist_skill_options,
                    'selected_profile_skill_names': selected_profile_skill_names,
                    'custom_profile_skills': custom_profile_skills,
                    'clinician_skills_payload_json': json.dumps(clinician_skills_payload),
                })
                return render(request, 'auction/profile.html', parameter)
        else:
            user_therapist_form = UserFormTherapist(instance=request.user)
            if 'submitted' in request.GET:
                submitted_profile = True
            parameter.update({
                'active_auctions_list': active_auctions_list,
                'past_auctions_list': past_auctions_list,
                'user_therapist_form': user_therapist_form,
                'user': user,
                'tickets': tickets,
                'joined_raffles': joined_raffles,
                'active_raffles': active_raffles,
                'referral_link': referral_link,
                'successful_referrals': successful_referrals,
                'ticket_history': ticket_history,
                'next_award_date': parameter.get('next_award_date'),
                'therapist_offer_history': therapist_offer_history,
                'skill_options': therapist_skill_options,
                'selected_profile_skill_names': selected_profile_skill_names,
                'custom_profile_skills': custom_profile_skills,
                'clinician_skills_payload_json': json.dumps(clinician_skills_payload),
            })
            return render(request, 'auction/profile.html', parameter)


def view_auction(request, auction_id):
    admin = AdminSetting.objects.first()
    auction = Auction.objects.get(pk=auction_id)
    if auction.active and auction.auctionEnd is not None and auction.auctionEnd <= timezone.now():
        scheduled_tasks.auction_closed(str(auction.auctionID))
        auction.refresh_from_db()
    print(auction.comments)
    is_effectively_active = auction.is_effectively_active()
    if is_effectively_active:
        num_bids = Bid.objects.filter(auction=auction_id, active=True).count()
        num_biders = Bid.objects.values('user').filter(auction=auction_id, active=True).distinct().count()
    else:
        num_bids = Bid.objects.filter(auction=auction_id).count()
        num_biders = Bid.objects.values('user').filter(auction=auction_id).distinct().count()
    bids = Bid.objects.filter(auction=auction_id, active=True).annotate(Min('amount')).order_by('amount')
    payment_types = auction.get_payment_types_list()
    payment_type = auction.get_primary_payment_type()
    allow_fee_split = 'Fee Split' in payment_types
    allow_flat_fee = 'Flat Fee' in payment_types
    can_place_offer = (
        request.user.is_authenticated
        and hasattr(request.user, 'account')
        and request.user.account.userType == auction.type
        and is_effectively_active
    )
    auction_change = False
    submitted = False
    max_bid = 0
    assessments = auction.assessmentCost is not None
    treatments = auction.treatmentCost is not None
    can_review_offers = (
        request.user.is_authenticated
        and hasattr(request.user, 'account')
        and auction.clinic.user_id == request.user.id
        and not auction.deleted
        and not auction.closed
        and (auction.active or auction.is_closed_waiting())
    )
    decline_all_offers_option = bool(can_review_offers and (auction.is_closed_waiting() or auction.is_in_clinic_review_window()))
    clinic_offer_rows = []
    required_skill_rows = auction.get_required_skill_rows()
    public_perk_rows = auction.get_public_perk_rows()
    private_perk_rows = auction.get_private_perk_rows()
    raw_listing_images = []
    for image_field_name in ('imageOne', 'imageTwo', 'imageThree', 'imageFour'):
        image_field_value = getattr(auction.clinic, image_field_name, None)
        image_name = str(getattr(image_field_value, 'name', image_field_value) or '').strip()
        if not image_name:
            continue
        if image_name.lower() in ('default.jpg', 'images/default.jpg'):
            continue
        raw_listing_images.append(image_name)

    listing_images = []
    for image_name in raw_listing_images:
        image_url = image_name if image_name.startswith('/media/') else f"/media/{image_name}"
        if image_url not in listing_images:
            listing_images.append(image_url)

    if len(listing_images) == 0:
        listing_images = ['/media/images/no-image.jpg']

    listing_image_count = len(listing_images)
    clinician_profile_skills = []
    finalize_skill_rows = []

    if can_place_offer and hasattr(request.user, 'account'):
        clinician_profile_skills = request.user.account.get_clinician_skill_names()
        profile_skill_set = {name.lower() for name in clinician_profile_skills}
        for skill_row in required_skill_rows:
            skill_name = _clean_text(skill_row.get('name'))
            if skill_name:
                finalize_skill_rows.append({
                    'name': skill_name,
                    'requirement': skill_row.get('requirement') or 'Required',
                    'selected': skill_name.lower() in profile_skill_set,
                })

    if can_review_offers:
        grouped_offers = {}
        review_bids = Bid.objects.filter(auction=auction, active=True).select_related('user').order_by('-created')

        for bid in review_bids:
            submission_key = str(bid.submissionGroup) if bid.submissionGroup else f"legacy-{bid.user_id}-{bid.created.isoformat()}-{bid.pk}"
            if submission_key not in grouped_offers:
                first_initial = (bid.user.first_name or '').strip()[:1]
                last_initial = (bid.user.last_name or '').strip()[:1]
                if not first_initial and not last_initial:
                    username_initials = (bid.user.username or 'U').strip()[:2].upper()
                    initials = username_initials if username_initials else 'U'
                else:
                    initials = f"{first_initial}{last_initial}".upper()

                grouped_offers[submission_key] = {
                    'hcp_initials': initials,
                    'row_dom_id': re.sub(r'[^a-zA-Z0-9_-]', '-', submission_key),
                    'submitted_at': bid.created,
                    'fee_split_offer': None,
                    'fee_split_bid_id': None,
                    'flat_fee_offer': None,
                    'flat_fee_bid_id': None,
                    'clinician_skill_names': bid.user.account.get_clinician_skill_names() if hasattr(bid.user, 'account') else [],
                    'selected_skill_names': bid.selectedSkills or [],
                    'skill_match': build_skill_match(required_skill_rows, bid.selectedSkills or []),
                    'additional_profile_skills': [],
                    'custom_profile_skills': [],
                }

                if hasattr(bid.user, 'account'):
                    profile_skills = bid.user.account.get_clinician_skill_names()
                    selected_skills_lower = {s.lower() for s in (bid.selectedSkills or [])}
                    bid_skill_options = get_clinician_skill_options_for_type(str(bid.user.account.userType or ''))
                    default_profile_skills_lower = {skill.lower() for skill in bid_skill_options}
                    grouped_offers[submission_key]['additional_profile_skills'] = [
                        s for s in profile_skills if s.lower() not in selected_skills_lower
                    ]
                    grouped_offers[submission_key]['custom_profile_skills'] = [
                        s for s in profile_skills
                        if s.lower() not in default_profile_skills_lower and not suppress_legacy_default_skill_for_type(str(bid.user.account.userType or ''), s)
                    ]

            if bid.offerType == 'Fee Split':
                grouped_offers[submission_key]['fee_split_offer'] = f"{int(bid.amount)}%"
                grouped_offers[submission_key]['fee_split_bid_id'] = str(bid.bidID)
            elif bid.offerType == 'Flat Fee':
                flat_fee_amount = f"${int(bid.amount)}"
                if auction.flatFeeType == 'hourly':
                    flat_fee_amount += '/hr'
                grouped_offers[submission_key]['flat_fee_offer'] = flat_fee_amount
                grouped_offers[submission_key]['flat_fee_bid_id'] = str(bid.bidID)

        clinic_offer_rows = list(grouped_offers.values())

    if num_bids > 0 and auction.currentLowBid is not None and auction.minimumBidIncrement is not None:
        diff = auction.currentLowBid - auction.minimumBidIncrement
        if diff > 0 and diff % auction.minimumBidIncrement == 0:
                max_bid = diff
        elif diff > 0 and diff % auction.minimumBidIncrement != 0:
            max_bid = auction.currentLowBid - (diff % auction.minimumBidIncrement)
    else:
        max_bid = 0

    if request.method == 'POST':
        print('post')
        if can_review_offers and request.POST.get('declineAllOffersAction') == '1':
            active_bids = list(Bid.objects.filter(auction=auction, active=True).select_related('user'))

            auction.winner = None
            auction.winningPrice = None
            auction.currentLowBid = None
            auction.active = False
            auction.waitingCloseout = False
            auction.closed = True
            auction.modified = timezone.now()
            auction.modifiedBy = request.user
            auction.save()

            Bid.objects.filter(auction=auction, active=True).update(active=False)

            if admin.sendEmails:
                clinic_email = _resolve_user_email(auction.clinic.user) if auction.clinic and auction.clinic.user else ''
                if clinic_email:
                    try:
                        send_mail(
                            subject='Listing Closed - No Candidate Selected',
                            message='',
                            html_message=emails.clinic_manual_no_offer_accepted(
                                str(auction.clinic.clinicName),
                                auction.placementStart,
                                auction.placementEnd,
                                auction.auctionID,
                            ),
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=(clinic_email, 'info@travelingtherapist.ca'),
                        )
                    except Exception:
                        logger.warning('Healthcare facility no-candidate email failed to send for listing closeout.')

                emailed = set()
                for bid in active_bids:
                    clinician_user = bid.user
                    clinician_email = _resolve_user_email(clinician_user)
                    if not clinician_email or clinician_email in emailed:
                        continue

                    emailed.add(clinician_email)
                    try:
                        send_mail(
                            subject='Listing Update',
                            message='',
                            html_message=emails.therapist_auction_end_lose(
                                clinician_user.first_name,
                                clinician_user.last_name,
                                auction.clinic.clinicName,
                                auction.placementStart,
                                auction.placementEnd,
                            ),
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=(clinician_email, 'info@travelingtherapist.ca'),
                        )
                    except Exception:
                        logger.warning('Clinician no-selection update email failed to send during listing closeout.')

            messages.success(request, 'Listing closed without accepting an offer. A flat invoice of $50 will be issued and you may relist this placement for free.')
            return HttpResponseRedirect('/auction/' + str(auction.auctionID))

        if can_review_offers and request.POST.get('acceptOfferAction') == '1':
            selected_bid_id = (request.POST.get('selectedOfferBidId') or '').strip()

            if not selected_bid_id:
                messages.error(request, 'Please select an offer before confirming.')
                return HttpResponseRedirect('/auction/' + str(auction.auctionID))

            selected_bid = Bid.objects.filter(bidID=selected_bid_id, auction=auction, active=True).select_related('user').first()
            if selected_bid is None:
                messages.error(request, 'The selected offer is no longer available.')
                return HttpResponseRedirect('/auction/' + str(auction.auctionID))

            active_bids = list(Bid.objects.filter(auction=auction, active=True).select_related('user'))

            auction.winner = selected_bid.user
            auction.winningPrice = selected_bid.amount
            auction.currentLowBid = selected_bid.amount
            auction.active = False
            auction.waitingCloseout = False
            auction.closed = True
            auction.modified = timezone.now()
            auction.modifiedBy = request.user
            auction.save()

            Bid.objects.filter(auction=auction, active=True).update(active=False)

            if admin.sendEmails:
                clinic_email = _resolve_user_email(auction.clinic.user) if auction.clinic and auction.clinic.user else ''
                if clinic_email:
                    try:
                        send_mail(
                            subject='Candidate Selected for Your Listing',
                            message='',
                            html_message=emails.offer_accepted(
                                str(auction.clinic.clinicName),
                                auction.placementStart,
                                auction.placementEnd,
                            ),
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=(clinic_email, 'info@travelingtherapist.ca'),
                        )
                    except Exception:
                        logger.warning('Clinic selected-candidate email failed to send.')

                winning_email = _resolve_user_email(selected_bid.user)
                if winning_email:
                    try:
                        send_mail(
                            subject='Congratulations! Your Offer Has Been Accepted!',
                            message='',
                            html_message=emails.therapist_auction_end_win(
                                selected_bid.user.first_name,
                                selected_bid.user.last_name,
                                auction.clinic.clinicName,
                                auction.placementStart,
                                auction.placementEnd,
                            ),
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=(winning_email, 'info@travelingtherapist.ca'),
                        )
                    except Exception:
                        logger.warning('Winning clinician email failed to send.')

                emailed = set([winning_email]) if winning_email else set()
                for bid in active_bids:
                    if bid.user_id == selected_bid.user_id:
                        continue
                    clinician_email = _resolve_user_email(bid.user)
                    if not clinician_email or clinician_email in emailed:
                        continue

                    emailed.add(clinician_email)
                    try:
                        send_mail(
                            subject='Listing Update',
                            message='',
                            html_message=emails.therapist_auction_end_lose(
                                bid.user.first_name,
                                bid.user.last_name,
                                auction.clinic.clinicName,
                                auction.placementStart,
                                auction.placementEnd,
                            ),
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=(clinician_email, 'info@travelingtherapist.ca'),
                        )
                    except Exception:
                        logger.warning('Non-selected clinician email failed to send.')

            offer_label = f"${int(selected_bid.amount)}" if selected_bid.offerType == 'Flat Fee' else f"{int(selected_bid.amount)}%"
            messages.success(request, f"Offer accepted: {selected_bid.offerType} {offer_label}.")
            return HttpResponseRedirect('/auction/' + str(auction.auctionID))

        flat_fee_raw = (request.POST.get('flatFeeAmount') or '').strip()
        fee_split_raw = (request.POST.get('feeSplitAmount') or '').strip()
        form = BidForm(payment_type=payment_type)
        errors = []
        bids_to_create = []
        submission_group = uuid.uuid4()
        previous_bid_count = Bid.objects.filter(user=request.user, auction=auction).count()
        selected_offer_skills = parse_offer_selected_skills_payload(request.POST.get('offerSelectedSkillsPayload', '[]'))

        def parse_offer_amount(raw_value, offer_type):
            if raw_value in (None, ''):
                return None
            try:
                decimal_value = Decimal(str(raw_value))
            except (InvalidOperation, ValueError, TypeError):
                return 'invalid'

            if offer_type == 'Flat Fee' and auction.flatFeeType == 'total_contract':
                if decimal_value < Decimal('1'):
                    return 'invalid-total-contract-minimum'
                if decimal_value != decimal_value.to_integral_value(rounding=ROUND_HALF_UP):
                    return 'invalid-total-contract-integer'

            rounded_value = decimal_value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
            return int(rounded_value)

        if allow_flat_fee and flat_fee_raw:
            flat_fee_amount = parse_offer_amount(flat_fee_raw, 'Flat Fee')
            if flat_fee_amount == 'invalid':
                errors.append('Flat fee offers must be valid numbers.')
            elif flat_fee_amount == 'invalid-total-contract-minimum':
                errors.append('Total contract flat fee offers must be at least $1.')
            elif flat_fee_amount == 'invalid-total-contract-integer':
                errors.append('Total contract flat fee offers must be whole-dollar amounts.')
            elif flat_fee_amount is not None and flat_fee_amount > 0:
                if auction.flatFeeType == 'hourly' and (flat_fee_amount < 15 or flat_fee_amount > 1000):
                    errors.append('Hourly flat fee offers must be between $15 and $1000.')
                else:
                    bids_to_create.append(Bid(
                        auction=auction,
                        user=request.user,
                        amount=flat_fee_amount,
                        offerType='Flat Fee',
                        submissionGroup=submission_group,
                        selectedSkills=selected_offer_skills,
                        active=True,
                        createdBy=request.user,
                    ))

        if allow_fee_split and fee_split_raw:
            fee_split_amount = parse_offer_amount(fee_split_raw, 'Fee Split')
            if fee_split_amount == 'invalid':
                errors.append('Fee split offers must be valid numbers.')
            elif fee_split_amount is not None and fee_split_amount > 0:
                if fee_split_amount > 100:
                    errors.append('Fee split offers must be less than or equal to 100%.')
                else:
                    bids_to_create.append(Bid(
                        auction=auction,
                        user=request.user,
                        amount=fee_split_amount,
                        offerType='Fee Split',
                        submissionGroup=submission_group,
                        selectedSkills=selected_offer_skills,
                        active=True,
                        createdBy=request.user,
                    ))

        if len(bids_to_create) == 0:
            errors.append('Please enter at least one offer before confirming.')

        if len(errors) == 0:
            for bid in bids_to_create:
                bid.save()

            primary_low_bid = auction.get_low_offer_amount(payment_type)
            if primary_low_bid is not None:
                auction.currentLowBid = primary_low_bid
                auction.minimumBidIncrement = set_bid_increment(primary_low_bid)
                auction_change = True

            if auction_change:
                auction.save()

            if hasattr(request.user, 'account'):
                request.user.account.add_tickets(5, f"Placed offer on listing {auction.auctionID}")
                messages.success(request, 'You have earned 5 raffle tickets for placing an offer!', extra_tags='ticket_earned')

            # Notify other clinicians who previously submitted offers on this listing.
            # Use one canonical helper path instead of legacy ranking-based notification logic.
            if len(bids_to_create) > 0:
                try:
                    scheduled_tasks.notify_clinicians_new_offer(auction.auctionID, bids_to_create[0].id)
                except Exception:
                    logger.warning('New-offer notification helper failed for listing %s.', auction.auctionID)

            if admin.sendEmails:
                try:
                    clinician_email = _resolve_user_email(request.user)
                    recipient_list = (clinician_email, 'info@travelingtherapist.ca') if clinician_email else ('info@travelingtherapist.ca',)
                    send_mail(
                        subject = 'Thank You for Your Offer',
                        message = '',
                        html_message = emails.therapist_auction_thank_you_bid(request.user.first_name, request.user.last_name, auction.clinic.clinicName, auction.auctionStart, auction.auctionID),
                        from_email = settings.EMAIL_HOST_USER,
                        recipient_list = recipient_list
                    )
                except:
                    print('Thank your for bidding email failed.')
                    logger.warning('Thank your for bidding email failed.')

            return HttpResponseRedirect('/auction/' + str(auction.auctionID))

        for error in errors:
            if not hasattr(form, 'cleaned_data'):
                form.cleaned_data = {}
            form.add_error(None, error)

        if form.errors:
            context = {
                'auction': auction,
                'form': form,
                'submitted': submitted,
                'num_bids': num_bids,
                'num_biders': num_biders,
                'payment_type': payment_type,
                'payment_types': payment_types,
                'allow_fee_split': allow_fee_split,
                'allow_flat_fee': allow_flat_fee,
                'assessments': assessments,
                'treatments': treatments,
                'can_place_offer': can_place_offer,
                'can_review_offers': can_review_offers,
                'clinic_offer_rows': clinic_offer_rows,
                'required_skill_rows': required_skill_rows,
                'public_perk_rows': public_perk_rows,
                'private_perk_rows': private_perk_rows,
                'listing_images': listing_images,
                'listing_image_count': listing_image_count,
                'finalize_skill_rows': finalize_skill_rows,
                'clinician_profile_skills': clinician_profile_skills,
                'decline_all_offers_option': decline_all_offers_option,
            }
            return render(request, 'auction/view_auction.html', context)
    else:
        form = BidForm(payment_type=payment_type)
        context = {
                'auction': auction,
                'form': form,
                'submitted': submitted,
                'num_bids': num_bids,
                'num_biders': num_biders,
                'payment_type': payment_type,
                'payment_types': payment_types,
                'allow_fee_split': allow_fee_split,
                'allow_flat_fee': allow_flat_fee,
                'assessments': assessments,
                'treatments': treatments,
                'can_place_offer': can_place_offer,
                'can_review_offers': can_review_offers,
                'clinic_offer_rows': clinic_offer_rows,
                'required_skill_rows': required_skill_rows,
                'public_perk_rows': public_perk_rows,
                'private_perk_rows': private_perk_rows,
                'listing_images': listing_images,
                'listing_image_count': listing_image_count,
                'finalize_skill_rows': finalize_skill_rows,
                'clinician_profile_skills': clinician_profile_skills,
                'decline_all_offers_option': decline_all_offers_option,
            }
        return render(request, 'auction/view_auction.html', context)
    
def get_auction_end(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    practice_area_valid = True

    demographic_obj = Demographic.objects.filter(auction__auctionID = auction_id)
    demographic_type = DemographicType.objects.all()
    demographic_types = []
    demographic_percentages = []

    practice_area_obj = PracticeArea.objects.filter(auction__auctionID = auction_id)
    practice_area_type = PracticeAreaType.objects.filter(userType = auction.type)
    practice_area_types = []
    practice_area_percentages = []

    for obj in demographic_obj:
        demographic_percentages.append(obj.percentage)

    for type in demographic_type:
        demographic_types.append(type.name)

    for obj in practice_area_obj:
        practice_area_percentages.append(obj.percentage)

    for type in practice_area_type:
        practice_area_types.append(type.name)

    # Check to make sure that there are the same number of labels as values
    if len(demographic_percentages) != len(demographic_types):
        demographic_percentages = [0]
        demographic_types = [0]

    # If the user has not entered any practice area pass this to the front-end so the graph is not shown 
    if len(practice_area_obj) == 0:
        practice_area_valid = False

    data = {
        'auctionStart': auction.auctionStart,
        'auctionEnd': auction.auctionEnd,
        'currentLowBid': auction.currentLowBid,
        'clinic': auction.clinic.clinicName,
        'demographic_percentages': demographic_percentages,
        'demographic_types': demographic_types,
        'practice_area_percentages': practice_area_percentages,
        'practice_area_types': practice_area_types,
        'practice_area_valid': practice_area_valid
    }
    return JsonResponse({'data': data})

def check_provinces(request):
    # if the auction is active and the province of the clinic and user do not match show a pop-up
    auction = Auction.objects.get(auctionID=request.GET['auctionID'])
    province_check = True
    if auction.clinic.province != '' or request.user.account.province != '':
        if auction.clinic.province != request.user.account.province and auction.active:
            province_check = False
    else:
        province_check = False
    return JsonResponse({'province_check': province_check})

def get_popups(request): 
    request_page = request.GET['page']
    click_id = request.GET['clickID']
    if click_id == '':
        click_id = None

    # Disable automatic listing-detail popups (non-click triggered).
    if request_page == 'View_Auction' and click_id is None:
        return JsonResponse({'title': '', 'message': ''})

    page = Page.objects.get(page = request_page)
    user = request.user
    message = ''
    title = ''
    popups = ''
    acknowledged = False
    if request.user.is_authenticated == True:
        popups = PopupMessage.objects.filter(page = page, active = True, clickID = click_id)
    else:
        popups = PopupMessage.objects.filter(page = page, active = True, show_unauthenticated_users = True, clickID = click_id)
    
    print('Popups'+str(popups))

    if popups.count() > 0: 
        for popup in popups:
            if request_page == 'View_Auction' and str(popup.title or '').strip().lower() == 'before you bid':
                continue
            try:
                message_acknowledgement = MessageAcknowledgement.objects.get(user = user, popup = popup)
                acknowledged = message_acknowledgement.acknowledged
            except:
                acknowledged = False
            
            # If click_id isn't blank then this refers to a pop-up that is clickable. This pop-up cannot be acknowledged because it is triggered by a click
            if acknowledged == False or click_id != None:
                message = message + " " + popup.message
                title = title + " " + popup.title

    return JsonResponse({'title': title, 'message': message})

def set_acknowledgement(request):
    if request.user.is_authenticated == True:
        request_page = request.POST['page']
        page = Page.objects.get(page = request_page)
        popups = PopupMessage.objects.filter(page = page, active = True)

        for popup in popups:
            message_acknowledgement = MessageAcknowledgement.objects.filter(user=request.user, popup = popup)
            print(message_acknowledgement.count())
            form = ''
            if message_acknowledgement.count() > 0:
                # There should only be one entry per pop-up per user
                form = MessageAcknowledgementForm(request.POST, instance=message_acknowledgement[0])
                print("in count > 0")
                if form.is_valid():
                    acknowledgement = form.save(commit=False)
                    acknowledgement.acknowledged = True
                    acknowledgement.save()
            else:
                form = MessageAcknowledgementForm(request.POST)
                print("in count = 0")
                if form.is_valid():
                    acknowledgement = form.save(commit=False)
                    acknowledgement.user = request.user
                    acknowledgement.popup = popup
                    acknowledgement.acknowledged = True
                    acknowledgement.save()
    return HttpResponse(json.dumps('Success'), content_type="application/json")

def get_all_auctions(request):
    auction_list = list(Auction.objects.filter((Q(active=True) | Q(closed=True) | Q(waitingCloseout=True)) & Q(deleted=False)).values())
    return JsonResponse({'data': auction_list})

def get_practice_types(request):
    practice_areas = PracticeAreaType.objects.filter(userType = request.POST['type'])
    max_practice_areas = practice_areas.count()
    practice_area_form_set = inlineformset_factory(Auction, PracticeArea, form=PracticeAreaForm, fields=('category', 'percentage'), max_num=max_practice_areas, extra=max_practice_areas, can_delete=False)
    formset_practice = practice_area_form_set(queryset=PracticeArea.objects.none())
    print(list(practice_areas))
    context = {
        'formset_practice': formset_practice,
        'practice_areas': list(practice_areas)
    }
    return render(request, 'auction/partials/practice_areas.html', context)

def get_active_auctions_clinic(request):
    active_auctions_list = ''
    if str(request.user.account.userType).split(' ')[-1] == "Clinic":
        active_auctions_list = list(Auction.objects.filter(active=True, closed=False, clinic=request.user.account, auctionEnd__gt=timezone.now()).values())
    else:
        query = 'SELECT DISTINCT AA.auctionID, AA.auctionStart, AA.auctionEnd, AA.currentLowBid, AB.bidID, AA.placementStart, AA.placementEnd, AA.clinic_id, AC.user_id, AC.clinicName, AC.city, AC.province, AC.about, AC.imageOne, AC.imageTwo, UT.name "userType" FROM auction_auction AA LEFT JOIN auction_bid AB ON AA.auctionID = AB.auction_id LEFT JOIN auction_account AC ON AA.clinic_id = AC.id LEFT JOIN auction_usertype UT ON AC.userType_id = UT.id WHERE AB.user_id = ' + str(request.user.account.user_id) + ' AND AA.active = 1 AND AA.closed = 0 AND AA.deleted = 0 GROUP BY auctionID, AA.placementStart, AA.placementEnd, AA.clinic_id, AC.user_id , AC.clinicName, AC.city, AC.about, AC.imageOne, AC.imageTwo, UT.name;'
        auction_list = Bid.objects.raw(query)
        active_auctions_list = []
        for a in auction_list:
            b = {}
            b.update({'auctionID': a.auctionID, 'auctionStart': a.auctionStart, 'auctionEnd': a.auctionEnd, 'currentLowBid': a.currentLowBid})
            active_auctions_list.append(b)
    return JsonResponse({'data': active_auctions_list})

def get_active_auctions_theraipist(request):
    user_id = str(request.user.id)
    active_auctions_list = list(Bid.objects.raw('SELECT DISTINCT AA.auctionID, AB.bidID, AA.placementStart, AA.placementEnd, AC.clinicName, AC.city, AC.province, AC.about, AC.imageOne, AC.imageTwo, UT.name "userType" FROM auction_auction AA JOIN auction_bid AB ON AA.auctionID = AB.auction_id JOIN auction_account AC ON AA.clinic_id = AC.user_id JOIN auction_usertype UT ON AC.userType_id = UT.id WHERE AB.user_id = ' + user_id + ' AND AA.active = 1 AND AA.closed = 0 AND AA.deleted = 0 GROUP BY auctionID;').values())
    return JsonResponse({'data': active_auctions_list})

def get_view_auction_data(request):
    auction = Auction.objects.get(auctionID=request.GET['auctionID'])
    if auction.is_effectively_active():
        num_bids = Bid.objects.filter(auction=request.GET['auctionID'], active=True).count()
        num_biders = Bid.objects.values('user').filter(auction=request.GET['auctionID'], active=True).distinct().count()
    else:
        num_bids = Bid.objects.filter(auction=request.GET['auctionID']).count()
        num_biders = Bid.objects.values('user').filter(auction=request.GET['auctionID']).distinct().count()
    payment_type = auction.get_primary_payment_type()
    payment_types = auction.get_payment_types_list()
    max_bid = 0
    matchting_types = False
    if num_bids > 0:
        next_offer_amount = auction.get_next_available_offer_amount(payment_type)
        max_bid = next_offer_amount if next_offer_amount is not None else 0
    if auction.type == request.user.account.userType:
        matchting_types = True
    return JsonResponse({
        'max_bid': max_bid,
        'currentLowBid': auction.get_low_offer_amount(payment_type),
        'flatFeeCurrentLowBid': auction.get_low_offer_amount('Flat Fee'),
        'feeSplitCurrentLowBid': auction.get_low_offer_amount('Fee Split'),
        'flatFeeMaxBid': auction.get_next_available_offer_amount('Flat Fee'),
        'feeSplitMaxBid': auction.get_next_available_offer_amount('Fee Split'),
        'minimumBidIncrement': auction.minimumBidIncrement,
        'auctionEnd': auction.auctionEnd,
        'reservePrice': auction.reservePrice,
        'paymentType': payment_type,
        'paymentTypes': payment_types,
        'flatFeeType': auction.flatFeeType,
        'active': auction.is_effectively_active(),
        'matchtingTypes': matchting_types,
        'numBids': num_bids,
        'numBiders': num_biders,
    })

def get_demographics(request, clinic_id):
    account = Account.objects.get(pk=clinic_id)
    data = {}
    # data.update({})
    print(account.demographic)
    return JsonResponse({'data': data})

def admin_summary(request):
    accounts_non_staff = Account.objects.filter(user__is_staff=False)
    accounts_staff = Account.objects.filter(user__is_staff=True)
    users_all = User.objects.all()
    auctions = Auction.objects.all()
    bids = Bid.objects.all()
    user_types = UserType.objects.all()
    user_types_count = {}

    print(users_all)

    for type in user_types:
        count = 0
        for account in accounts_non_staff:
            if account.userType == type:
                count = count + 1
        user_types_count[type] = count

    print(user_types_count)
            
    context = {
        'total_users_non_staff': accounts_non_staff.__len__,
        'total_users_staff': accounts_staff.__len__,
        'user_types_count': user_types_count,
        'auction_count': auctions.__len__,
        'bid_count': bids.__len__,
        'users': users_all
    }
    return render(request, 'auction/admin_summary.html', context)

@login_required(login_url='login')
def create_auction(request):
    if request.user.is_authenticated == False:
        return render(request, 'auction/create_auction.html', {})
    admin = AdminSetting.objects.first()
    # Not closed and not deleted counts any auctions that are active or have no status selected
    active_auctions_list = Auction.objects.filter(closed=False, deleted=False, clinic=request.user.account)
    last_auction = Auction.objects.filter(deleted=False, clinic=request.user.account).order_by('-created').first()
    remember_last_auction = Account.objects.filter(user=request.user).values().first()['remember_auction_data']
    submitted_auction = False
    parameter = {}
    selected = ''
    user_types = UserType.objects.filter(~Q(name='Clinic'))
    # If the user has selected remember previous data get their last selected auction type
    if active_auctions_list.count() > 0 and remember_last_auction:
        selected = last_auction.type
    max_auctions = admin
    max_demographics = DemographicType.objects.all().count()
    # Areas of practice are specific to a user type so get the user's type
    max_practice_areas = 0 #PracticeAreaType.objects.all().count()
    demographic_form_set = inlineformset_factory(Auction, Demographic, form=DemographicForm, fields=('category', 'percentage'), max_num=max_demographics, extra=max_demographics, can_delete=False, help_texts=None)
    practice_area_form_set = inlineformset_factory(Auction, PracticeArea, form=PracticeAreaForm, fields=('category', 'percentage'), max_num=max_practice_areas, extra=max_practice_areas, can_delete=False)
    account = Account.objects.get(user=request.user.id)
    if active_auctions_list.count() <= max_auctions.numAllowedAuctions:
        if request.method == "POST":
            form = AuctionForm(request.POST, request.FILES)
            account_form = AuctionAccountForm(request.POST, request.FILES, instance=account)
            formset_demographic = demographic_form_set(queryset=Demographic.objects.none())
            formset_practice = practice_area_form_set(queryset=PracticeArea.objects.none())

            # Listings must always have a clinic image source.
            if not account.imageOne:
                account.imageOne = 'default.jpg'
                account.save(update_fields=['imageOne'])

            print(form.errors)
            if form.is_valid():
                print('valid form')
                auction = form.save(commit=False)
                auction.requiredSkills = parse_required_skills_payload(request.POST.get('requiredSkillsPayload', '[]'))
                auction.negotiablePerks = parse_negotiable_perks_payload(request.POST.get('negotiablePerksPayload', '[]'))
                auction.clinic = request.user.account
                auction.auctionStart = datetime.datetime.now(pytz.timezone('America/Toronto'))
                auction.auctionEnd = datetime.datetime.now(pytz.timezone('America/Toronto')) + datetime.timedelta(seconds=admin.defaultAuctionLength)
                auction.closed = False
                auction.active = settings.DEFAULT_AUCTION_ACTIVE
                auction.deleted = False
                auction.createdBy = request.user
                auction.modifiedBy = request.user
                auction.auctionNumber = get_next_auction_number()
                print(auction.reservePrice)
                auction.save()
                formset_demographic = demographic_form_set(request.POST, instance=auction, queryset=Demographic.objects.none())
                formset_practice = practice_area_form_set(request.POST, instance=auction, queryset=PracticeArea.objects.none())
                print('AOP')
                
                if formset_practice.is_valid() and formset_demographic.is_valid():
                    formset_demographic.save()
                    # If AOP is populated save it
                    if request.POST.get("AOPPopulated", "") == 'Yes':
                        formset_practice.save()
                else:
                    print("Fail")
                    print(formset_demographic.errors)
                    print(formset_practice.errors)
                    return False

                if account_form.is_valid():
                    account_instance = account_form.save(commit=False)
                    account_instance.user = request.user
                    account_instance.save()
                else:
                    print("Fail")
                    print(account_form.errors)
                    return False
    
                parameter.update({
                'active_auctions_list': active_auctions_list,
                'form': form,
                'account_form': account_form,
                'formset_demographic': formset_demographic,
                'formset_practice': 'formset_practice',
                'submitted_auction': submitted_auction,
                'show_form': True,
                'user_types': user_types,
                'selected': selected,
                'listing_skill_options': LISTING_SKILL_OPTIONS,
                })
                # return render(request, 'auction/create_auction.html', parameter)

                if admin.sendEmails:
                    # Admin email
                    try:
                        send_mail(
                            subject = "Auction Created - Admin Details",
                            message = "",
                            html_message = emails.auction_created_admin(str(auction.clinic.clinicName), str(auction.clinic.city), str(auction.clinic.province), str(auction.clinic.user.email), str(auction.get_payment_type_label()), str(auction.flatFeeType), str(auction.auctionStart), str(auction.auctionEnd), str(auction.placementStart), str(auction.placementEnd), str(auction.auctionID)),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = ('info@travelingtherapist.ca',)
                        )
                    except:
                        print('Admin email failed to send for Listing Creation.')
                        logger.warning('Admin email failed to send for Listing Creation.')


                    # Clinic email
                    try:
                        send_mail(
                            subject = "Your Listing has Been Created",
                            message = "",
                            html_message = emails.clinic_auction_created(str(auction.clinic.clinicName)),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = (auction.clinic.user.email,)
                        )
                    except:
                        print('Healthcare facility email failed to send for Listing Creation.')
                        logger.warning('Healthcare facility email failed to send for Listing Creation.')

                    try:    
                        send_mail(
                            subject = "Your Listing has Been Created",
                            message = "",
                            html_message = "**ADMIN COPY**" + emails.clinic_auction_created(str(auction.clinic.clinicName)),
                            from_email = settings.EMAIL_HOST_USER,
                            recipient_list = ('info@travelingtherapist.ca', )
                        )
                    except:
                        print('Admin copy of healthcare facility email failed to send for Listing Creation.')
                        logger.warning('Admin copy of healthcare facility email failed to send for Listing Creation.')

                if auction.active:
                    scheduled_tasks.start(auction.auctionEnd.year, auction.auctionEnd.month, auction.auctionEnd.day, auction.auctionEnd.hour, auction.auctionEnd.minute, auction.auctionEnd.second, str(auction.auctionID))
                    if admin.sendEmails:
                        try:
                            scheduled_tasks.notify_all_clinicians_auction_live(str(auction.auctionID))
                        except Exception:
                            logger.warning('New listing broadcast failed for listing %s created as active.', auction.auctionID)
                
                # Reward the clinic with 5 tickets for creating a listing
                if hasattr(request.user, 'account'):
                    request.user.account.add_tickets(5, f"Created listing {auction.auctionID}")
                    messages.success(request, 'You have earned 5 raffle tickets for creating a job listing!', extra_tags='ticket_earned')
                
                return HttpResponseRedirect('/profile?submitted=True')
            else:
                print("else")
                parameter.update({
                    'active_auctions_list': active_auctions_list,
                    'form': form,
                    'account_form': account_form,
                    'formset_demographic': formset_demographic,
                    'formset_practice': formset_practice,
                    'submitted_auction': submitted_auction,
                    'show_form': True,
                    'user_types': user_types,
                    'selected': selected,
                    'listing_skill_options': LISTING_SKILL_OPTIONS,
                })
                return render(request, 'auction/create_auction.html', parameter)
        else:
            # New Form
            account_form = AuctionAccountForm(instance=account)
            if remember_last_auction:
                form = AuctionForm(instance=last_auction)
                formset_demographic = demographic_form_set(instance=last_auction)
                formset_practice = practice_area_form_set(instance=last_auction)
            else:
                form = AuctionForm()
                formset_demographic = demographic_form_set(queryset=None)
                formset_practice = practice_area_form_set(queryset=None)
            parameter.update({
                'active_auctions_list': active_auctions_list,
                'form': form,
                'account_form': account_form,
                'formset_demographic': formset_demographic,
                'formset_practice': formset_practice,
                'submitted_auction': submitted_auction,
                'show_form': True,
                'user_types': user_types,
                'selected': selected,
                'remember_last_auction': remember_last_auction,
                'listing_skill_options': LISTING_SKILL_OPTIONS,
            })
            return render(request, 'auction/create_auction.html', parameter)
    else:
        form = AuctionForm()
        parameter.update({
            'active_auctions_list': active_auctions_list,
            'show_form': False,
            'max_forms': max_auctions.numAllowedAuctions
        })
        return render(request, 'auction/create_auction.html', parameter)

def check_user_payment_type(request):
    user_type = UserType.objects.get(name=request.GET['name'])
    return JsonResponse({
        'feeSplit': user_type.feeSplit
    })

# @login_required(login_url='login')
# @transaction.atomic
def register(request):
    from django.db import transaction
    admin = AdminSetting.objects.first()
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterAcount(request.POST, request.FILES)
        accepted_terms = request.POST.get('termsAgreed') == '1'

        if not accepted_terms:
            form.add_error(None, 'You must read and agree to the Terms and Conditions before creating an account.')
            return render(request, 'auction/register.html', {
                'form': form,
                'user_type': form.cleaned_data.get('user_type'),
                'keep_terms_checked': False,
            })

        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    user.refresh_from_db()  # load the profile instance created by the signal
                    
                    # Set user fields
                    user.email = form.cleaned_data.get('username')
                    user.first_name = form.cleaned_data.get('first_name')
                    user.last_name = form.cleaned_data.get('last_name')
                    user.save()

                    # Set account fields
                    account = user.account
                    account.userType = form.cleaned_data.get('user_type')
                    account.city = form.cleaned_data.get('city')
                    account.province = form.cleaned_data.get('province')
                    account.country = 'Canada'
                    account.about = form.cleaned_data.get('about')
                    account.clinicWebsite = form.cleaned_data.get('clinicWebsite')
                    account.clinicName = form.cleaned_data.get('clinicName')
                    account.imageOne = form.cleaned_data.get('imageOne')
                    account.imageTwo = form.cleaned_data.get('imageTwo')
                    account.imageThree = form.cleaned_data.get('imageThree')
                    account.imageFour = form.cleaned_data.get('imageFour')
                    
                    # Referral logic
                    referral_code = request.session.get('referral_code')
                    if referral_code:
                        print(f"Registration: Found referral code {referral_code} in session")
                        try:
                            referrer_account = Account.objects.get(referral_code=referral_code)
                            referrer = referrer_account.user
                            
                            # Self-referral block
                            if referrer.email != user.email:
                                account.referred_by = referrer
                                # Use get_or_create to prevent IntegrityError on double-submit
                                Referral.objects.get_or_create(referrer=referrer, referred_user=user)
                                print(f"Registration: Referral linked for {user.username} (referred by {referrer.username})")
                            else:
                                print(f"Registration: Self-referral attempt blocked for {user.username}")
                        except Account.DoesNotExist:
                            print(f"Registration: Invalid referral code {referral_code}")
                        # Clean up session
                        del request.session['referral_code']

                    account.save()
                    print(f"Registration: Account saved for {user.username}")

                    # Trigger referral verification check immediately after registration
                    # This awards tickets and sends the referral success email to the referrer
                    awarded = account.check_and_award_referral()
                    print(f"Registration: check_and_award_referral returned {awarded}")
            except Exception as e:
                print(f"Registration Error: Transaction failed: {e}")
                logger.error(f"Registration Error: Transaction failed: {e}")
                # Re-render with form errors if possible, or just re-raise
                return render(request, 'auction/register.html', {
                    'form': form,
                    'error': 'An internal error occurred. Please try again.',
                    'keep_terms_checked': True,
                })
            
            # Recaptcha and Emails move OUTSIDE the transaction to prevent rollbacks on network issues
            recaptcha_response = request.POST.get('g-recaptcha-response')
            data = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
            }
            try:
                r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
                result = r.json()
                print(f"Registration: Recaptcha result: {result}")
            except Exception as e:
                print(f"Registration: Recaptcha request failed: {e}")
                result = {'success': True} # Fail open if recaptcha service is down

            if admin.sendEmails:
                print(f"Registration: Attempting to send welcome email to {user.email}")
                if str(account.userType).split(' ')[-1] == "Clinic":
                    # Clinic email
                    try:
                        send_mail(
                                subject = "Welcome to the Traveling Therapist",
                                message = "",
                                html_message = emails.clinic_welcome(account.clinicName),
                                from_email = settings.EMAIL_HOST_USER,
                                recipient_list = [user.email],
                            )
                        print(f"Registration: Welcome email sent to clinic {user.email}")
                    except Exception as e:
                        print(f'Registration Error: Healthcare facility email failed: {e}')
                        logger.warning(f'Registration Error: Healthcare facility email failed: {e}')

                    try:
                        subject_content = "Welcome to the Traveling Therapist"
                        if not result.get('success') or result.get('score', 1.0) <= .5:
                            subject_content = "!!!!Welcome to the Traveling Therapist - POTENTIAL BOT!!!!!"
                        
                        send_mail(
                                subject = subject_content,
                                message = "",
                                html_message = "**ADMIN COPY** " + ("POTENTIAL BOT!!!!!" if "BOT" in subject_content else "") + emails.clinic_welcome(account.clinicName),
                                from_email = settings.EMAIL_HOST_USER,
                                recipient_list = ["info@travelingtherapist.ca"],
                            )
                    except Exception as e:
                        print(f'Registration Error: Admin copy (clinic) failed: {e}')
                else:
                    # Therapist email
                    try:
                        send_mail(
                                subject = "Welcome to the Traveling Therapist",
                                message = "",
                                html_message = emails.therapist_welcome(user.first_name, user.last_name),
                                from_email = settings.EMAIL_HOST_USER,
                                recipient_list = [user.email]
                            )
                        print(f"Registration: Welcome email sent to therapist {user.email}")
                    except Exception as e:
                        print(f'Registration Error: Therapist email failed: {e}')
                        logger.warning(f'Registration Error: Therapist email failed: {e}')

                    try:
                        subject_content = "Welcome to the Traveling Therapist"
                        if not result.get('success') or result.get('score', 1.0) <= .5:
                            subject_content = "!!!!Welcome to the Traveling Therapist - POTENTIAL BOT!!!!!"
                        
                        send_mail(
                                subject = subject_content,
                                message = "",
                                html_message = "**ADMIN COPY** " + ("POTENTIAL BOT!!!!!" if "BOT" in subject_content else "") + emails.therapist_welcome(user.first_name, user.last_name),
                                from_email = settings.EMAIL_HOST_USER,
                                recipient_list = ["info@travelingtherapist.ca"]
                            )
                    except Exception as e:
                        print(f'Registration Error: Admin copy (therapist) failed: {e}')
                    
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request, 'Welcome! You have earned 5 raffle tickets for signing up!', extra_tags='ticket_earned')
            return redirect('index')
        else:
            print("not valid")
            return render(request, 'auction/register.html', {
                'form': form,
                'user_type': form.cleaned_data.get('user_type'),
                'keep_terms_checked': True,
            })
    else:
        print('outside')
        form = RegisterAcount(None)
        return render(request, 'auction/register.html', {'form': form, 'keep_terms_checked': False})
    
# -------------- Login --------------
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('index')
        else:
            messages.error(request, ("Login was unsuccessful. Please check your email and password."))
            return redirect('login')
    else:
        return render(request, 'auction/login.html', {'path': 'login'})

def logout_user(request):
    logout(request)
    # messages.success(request, ("Logged out"))
    return redirect('index')

def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    reset_link = f"{emails.EMAIL_BASE_LINK}/reset/{uid}/{token}/"
                    plain_message = f"Use the following link to reset your password: {reset_link}"
                    html_email = emails.password_reset(user.first_name, reset_link)
                    try:
                        send_mail(subject, plain_message, 'info@travelingtherapist.ca', [user.email], html_message=html_email, fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="auction/password/password_reset.html", context={"password_reset_form": password_reset_form})

# -------------- Utility --------------
def set_bid_increment(amount):
    min_increment = 0
    if amount <= 100:
        min_increment = 1
    elif amount > 100 and amount <= 10000:
        min_increment = 100
    elif amount > 10000 and amount <= 25000:
        min_increment = 250
    else:
        min_increment = 500
    return min_increment

def get_next_auction_number():
    number = Number.objects.get(category='auction_id')
    number.currentValue = number.currentValue + 1
    number.save()
    return number.currentValue + 1

# service benefits - static page
def service_benefits_page(request):
    return render(request, 'auction/service_benefits.html', {})

# why use - static page
def what_is_TTT(request):
    return render(request, 'auction/what_is_TTT.html', {})

def hiring_with_the_traveling_therapist_view(request):
    return render(request, 'auction/hiring_with_the_traveling_therapist.html', {})

def retirement_home_hiring_guide(request):
    return render(request, 'auction/retirement_home_hiring_guide.html', {'path': 'retirement-home-hiring-guide'})

def job_boards(request):
    return render(request, 'auction/job_boards.html', {'path': 'job-boards'})

def private_clinic_hiring_guide(request):
    return render(request, 'auction/private_clinic_hiring_guide.html', {'path': 'private-clinic-hiring-guide'})

def agency_comparison(request):
    return render(request, 'auction/agency_comparison.html', {'path': 'agency-comparison'})

def referrals_and_networks(request):
     return render(request, "auction/referrals_and_networks.html", {'path': 'referrals-and-networks'})

def referral_program(request):
    referral_link = ""
    if request.user.is_authenticated:
        referral_link = request.user.account.get_referral_link()
    return render(request, "auction/referral_program.html", {'path': 'facility-referral', 'referral_link': referral_link})

def what_are_raffles(request):
    return render(request, 'auction/what_are_raffles.html', {'path': 'what-are-raffles'})

@login_required(login_url='login')
def surveys(request):
    """
    Role-based surveys page. 
    Redirects unauthenticated users to login (via @login_required(login_url='login')).
    Filters visible surveys based on user type.
    """
    user_type = request.user.account.get_split_user_type()
    context = {
        'user_type': user_type,
        'path': 'surveys'
    }
    return render(request, 'auction/surveys.html', context)


def is_user_staff(u):
    return u.is_staff

@login_required(login_url='login')
@user_passes_test(is_user_staff)
def admin_raffle_management(request):
    """
    Raffle Management Dashboard for Admins.
    Organizes raffles into Live, Scheduled, and Ended streams.
    Calculates ticket distribution metrics for each raffle.
    """
    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)

    # 1. LIVE RAFFLES: Active, Start in past/present, End in future
    live_raffles_qs = Raffle.objects.filter(
        active=True, 
        startDate__lte=now, 
        endDate__gt=now
    ).order_by('endDate')

    # 2. SCHEDULED RAFFLES: Active, Start in future
    scheduled_raffles_qs = Raffle.objects.filter(
        active=True, 
        startDate__gt=now
    ).order_by('startDate')

    # 3. INACTIVE RAFFLES: Not active, and either haven't ended yet or were never started
    inactive_raffles_qs = Raffle.objects.filter(
        active=False,
        endDate__gt=now
    ).order_by('-startDate')

    # 4. RECENTLY ENDED RAFFLES: End in past, within last 7 days
    ended_raffles_qs = Raffle.objects.filter(
        endDate__lte=now,
        endDate__gte=seven_days_ago
    ).order_by('-endDate')

    def get_raffle_stats(raffles_qs):
        processed = []
        for raffle in raffles_qs:
            entries = RaffleEntry.objects.filter(raffle=raffle).select_related('user__account__userType')
            total_tickets = entries.aggregate(Sum('tickets_added'))['tickets_added__sum'] or 0
            
            clinics_tickets = 0
            clinicians_tickets = 0
            admin_total = 0
            clinics_seen = set()
            clinicians_seen = set()
            sub_breakdown = {} # { 'Physiotherapist': 10, ... }
            clinic_breakdown = {} # { 'Clinic Name A': 5, ... }

            for entry in entries:
                if entry.user.is_superuser or entry.user.is_staff:
                    admin_total += entry.tickets_added
                    continue
                    
                u_type = entry.user.account.userType.name if entry.user.account.userType else "Unknown"
                is_clinic = "Clinic" in u_type
                
                if is_clinic:
                    clinics_tickets += entry.tickets_added
                    clinics_seen.add(entry.user.id)
                    clinic_name = entry.user.account.clinicName
                    if not clinic_name:
                         clinic_name = f"{entry.user.first_name} {entry.user.last_name}".strip()
                    if not clinic_name:
                         clinic_name = entry.user.username
                    clinic_breakdown[clinic_name] = clinic_breakdown.get(clinic_name, 0) + entry.tickets_added
                else:
                    clinicians_tickets += entry.tickets_added
                    clinicians_seen.add(entry.user.id)
                    sub_breakdown[u_type] = sub_breakdown.get(u_type, 0) + entry.tickets_added

            processed.append({
                'obj': raffle,
                'total_tickets': total_tickets,
                'clinics_count': len(clinics_seen),
                'clinics_tickets': clinics_tickets,
                'clinicians_count': len(clinicians_seen),
                'clinicians_total': clinicians_tickets,
                'admin_total': admin_total,
                'sub_breakdown': sub_breakdown,
                'clinic_breakdown': clinic_breakdown,
                'clinics_perc': (clinics_tickets / total_tickets * 100) if total_tickets > 0 else 0,
                'clinicians_perc': (clinicians_tickets / total_tickets * 100) if total_tickets > 0 else 0,
                'admin_perc': (admin_total / total_tickets * 100) if total_tickets > 0 else 0,
            })
        return processed

    context = {
        'path': 'admin-raffle-management',
        'live_raffles': get_raffle_stats(live_raffles_qs),
        'inactive_raffles': get_raffle_stats(inactive_raffles_qs),
        'scheduled_raffles': get_raffle_stats(scheduled_raffles_qs),
        'ended_raffles': get_raffle_stats(ended_raffles_qs),
    }
    return render(request, 'auction/admin_raffle_management.html', context)

@login_required(login_url='login')
@user_passes_test(is_user_staff)
def admin_raffle_api(request):
    """
    AJAX API for Raffle CRUD and Administrative Actions.
    Handles both JSON and FormData (for image uploads).
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

    try:
        # Determine how to parse data based on Content-Type
        if request.content_type.startswith('multipart/form-data'):
            data = request.POST
            is_form_data = True
        else:
            data = json.loads(request.body)
            is_form_data = False

        action = data.get('action')
        raffle_id = data.get('raffle_id')

        if action == 'delete':
            raffle = Raffle.objects.get(id=raffle_id)
            if raffle.cronID:
                from . import scheduled_tasks
                try: scheduled_tasks.remove_cron_job(raffle.cronID)
                except: pass
            raffle.delete()
            return JsonResponse({'status': 'success', 'message': 'Raffle deleted successfully.'})

        elif action == 'toggle_status':
            raffle = Raffle.objects.get(id=raffle_id)
            raffle.active = not raffle.active
            raffle.save()
            return JsonResponse({'status': 'success', 'message': f'Raffle {"activated" if raffle.active else "deactivated"} successfully.'})

        elif action == 'force_draw':
            from . import scheduled_tasks
            scheduled_tasks.execute_raffle_draw_task(raffle_id=raffle_id)
            return JsonResponse({'status': 'success', 'message': 'Manual draw executed successfully.'})

        elif action in ['create', 'edit']:
            title = data.get('title')
            description = data.get('description')
            start_date_str = data.get('startDate')
            end_date_str = data.get('endDate')
            tickets_required = data.get('tickets_required', 1)
            target_audience = data.get('target_audience', 'Both')
            value_text = data.get('value_text', '')

            # Parse dates (expecting ISO format from JS)
            from django.utils.dateparse import parse_datetime
            start_date = parse_datetime(start_date_str)
            end_date = parse_datetime(end_date_str)

            if action == 'edit':
                raffle = Raffle.objects.get(id=raffle_id)
            else:
                raffle = Raffle()

            raffle.title = title
            raffle.description = description
            raffle.startDate = start_date
            raffle.endDate = end_date
            raffle.tickets_required = tickets_required
            raffle.target_audience = target_audience
            raffle.value_text = value_text

            # Handle Image Upload if present in request.FILES
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                # Server-side size validation (5MB)
                if image_file.size > 5 * 1024 * 1024:
                    return JsonResponse({'status': 'error', 'message': 'Image size too large - please select an image less than 5mb'})
                raffle.image = image_file

            raffle.save()

            # Handle cron rescheduling
            from . import scheduled_tasks
            if raffle.cronID:
                try: scheduled_tasks.remove_cron_job(raffle.cronID)
                except: pass
            
            if raffle.active and raffle.endDate:
                scheduled_tasks.start_raffle(raffle.endDate, str(raffle.id))

            return JsonResponse({'status': 'success', 'message': f'Raffle {"updated" if action == "edit" else "created"} successfully.'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Unknown action.'})


def join_raffle(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'You must be logged in to enter a raffle.'})
        
        try:
            data = json.loads(request.body)
            raffle_title = data.get('raffle_title')
            tickets_to_add = int(data.get('ticket_count', 0))
            
            if tickets_to_add <= 0:
                return JsonResponse({'status': 'error', 'message': 'Please enter a valid number of tickets.'})
                
            account = request.user.account
            
            # Check balance
            if account.numTickets < tickets_to_add:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'You only have {account.numTickets} tickets available.'
                })
            
            raffle = Raffle.objects.get(title=raffle_title, active=True)

            # MULTIPLIER VALIDATION
            if tickets_to_add % raffle.tickets_required != 0:
                return JsonResponse({
                    'status': 'error', 
                    'message': f'This raffle requires multiples of {raffle.tickets_required} tickets per entry.'
                })
            
            # Deduct tickets via ledger
            account.add_tickets(-tickets_to_add, f"Raffle entry: {raffle.title}")
            
            # Create or update entry
            entry, created = RaffleEntry.objects.get_or_create(
                user=request.user,
                raffle=raffle
            )
            entry.tickets_added += tickets_to_add
            entry.save()
            
            return JsonResponse({
                'status': 'success', 
                'message': f'Successfully added {tickets_to_add} tickets to {raffle.title}.',
                'new_balance': account.numTickets
            })
            
        except Raffle.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Raffle not found or is no longer active.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


# Platform Updates Views
def platform_updates_hub(request):
    return render(request, 'auction/platform_updates_hub.html')

def update_v10_0(request):
    return render(request, 'auction/updates/v10_0.html')

def update_v9_0(request):
    return render(request, 'auction/updates/v9_0.html')

def update_v8_0(request):
    return render(request, 'auction/updates/v8_0.html')

def update_v7_0(request):
    return render(request, 'auction/updates/v7_0.html')

def update_v6_1(request):
    return render(request, 'auction/updates/v6_1.html')

def update_v6_0(request):
    return render(request, 'auction/updates/v6_0.html')