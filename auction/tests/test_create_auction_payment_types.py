from datetime import timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from auction.forms import AuctionForm
from auction.models import Account, AdminSetting, Auction, Bid, PaymentType, UserType


class AuctionPaymentTypeFormTests(TestCase):
	def setUp(self):
		self.clinic_user_type = UserType.objects.create(name='Physiotherapy Clinic')
		self.clinician_user_type = UserType.objects.create(name='Physiotherapist', feeSplit=True)
		self.restricted_clinician_user_type = UserType.objects.create(name='Restricted Clinician', feeSplit=False)
		self.fee_split = PaymentType.objects.create(name='Fee Split')
		self.flat_fee = PaymentType.objects.create(name='Flat Fee')

		self.user = User.objects.create_user(
			username='clinic@example.com',
			email='clinic@example.com',
			password='password123',
		)
		self.account = Account.objects.get(user=self.user)
		self.account.clinicName = 'Test Clinic'
		self.account.userType = self.clinic_user_type
		self.account.save()

	def _base_form_data(self):
		start_date = (timezone.localdate() + timedelta(days=7)).isoformat()
		end_date = (timezone.localdate() + timedelta(days=21)).isoformat()

		return {
			'type': self.clinician_user_type.pk,
			'placementStart': start_date,
			'placementEnd': end_date,
			'mondayStart': '09:00',
			'mondayEnd': '17:00',
			'tuesdayStart': '',
			'tuesdayEnd': '',
			'wednesdayStart': '',
			'wednesdayEnd': '',
			'thursdayStart': '',
			'thursdayEnd': '',
			'fridayStart': '',
			'fridayEnd': '',
			'saturdayStart': '',
			'saturdayEnd': '',
			'sundayStart': '',
			'sundayEnd': '',
			'comments': 'Test listing',
		}

	def test_payment_types_require_a_selection_and_flat_fee_subtype(self):
		data = self._base_form_data()
		data['paymentTypesSelection'] = []
		form = AuctionForm(data=data)

		self.assertFalse(form.is_valid())
		self.assertIn('Please select at least one payment type.', form.non_field_errors())

		data = self._base_form_data()
		data['paymentTypesSelection'] = ['Flat Fee']
		form = AuctionForm(data=data)

		self.assertFalse(form.is_valid())
		self.assertIn('Please select how flat fee offers should be priced.', form.non_field_errors())

	def test_payment_type_selection_saves_combined_state(self):
		data = self._base_form_data()
		data['paymentTypesSelection'] = ['Fee Split', 'Flat Fee']
		data['flatFeeType'] = 'hourly'
		form = AuctionForm(data=data)

		self.assertTrue(form.is_valid(), form.errors)
		auction = form.save(commit=False)

		self.assertEqual(auction.paymentTypes, 'Fee Split,Flat Fee')
		self.assertEqual(auction.flatFeeType, 'hourly')
		self.assertEqual(auction.paymentType.name, 'Fee Split')

	def test_desired_guidance_fields_save_for_matching_payment_types(self):
		data = self._base_form_data()
		data['paymentTypesSelection'] = ['Fee Split', 'Flat Fee']
		data['flatFeeType'] = 'hourly'
		data['desiredFeeSplitPercentage'] = 65
		data['desiredFlatFeeHourly'] = 90
		form = AuctionForm(data=data)

		self.assertTrue(form.is_valid(), form.errors)
		auction = form.save(commit=False)
		self.assertEqual(auction.desiredFeeSplitPercentage, 65)
		self.assertEqual(auction.desiredFlatFeeHourly, 90)
		self.assertIsNone(auction.desiredFlatFeeTotalContract)

	def test_restricted_user_type_cannot_select_fee_split(self):
		data = self._base_form_data()
		data['type'] = self.restricted_clinician_user_type.pk
		data['paymentTypesSelection'] = ['Fee Split']
		form = AuctionForm(data=data)

		self.assertFalse(form.is_valid())
		self.assertIn(
			'Fee Split is not available for Restricted Clinician. Please choose Flat Fee.',
			form.non_field_errors(),
		)

	def test_placement_start_must_be_tomorrow_or_later(self):
		data = self._base_form_data()
		data['paymentTypesSelection'] = ['Flat Fee']
		data['flatFeeType'] = 'hourly'
		data['placementStart'] = timezone.localdate().isoformat()
		data['placementEnd'] = (timezone.localdate() + timedelta(days=3)).isoformat()
		form = AuctionForm(data=data)

		self.assertFalse(form.is_valid())
		self.assertIn('The clinician start date must be tomorrow or later.', form.non_field_errors())

	def test_default_placement_start_is_tomorrow(self):
		form = AuctionForm()
		tomorrow = timezone.localdate() + timedelta(days=1)

		self.assertEqual(form.fields['placementStart'].widget.attrs.get('min'), tomorrow.isoformat())
		self.assertEqual(form.fields['placementStart'].widget.attrs.get('value'), tomorrow.isoformat())


class AuctionPaymentTypeHelperTests(TestCase):
	def setUp(self):
		self.clinic_user_type = UserType.objects.create(name='Physiotherapy Clinic')
		self.clinician_user_type = UserType.objects.create(name='Physiotherapist')
		self.fee_split = PaymentType.objects.create(name='Fee Split')
		self.flat_fee = PaymentType.objects.create(name='Flat Fee')

		self.user = User.objects.create_user(
			username='clinic2@example.com',
			email='clinic2@example.com',
			password='password123',
		)
		self.account = Account.objects.get(user=self.user)
		self.account.clinicName = 'Helper Clinic'
		self.account.userType = self.clinic_user_type
		self.account.save()

	def test_combined_payment_label_includes_flat_fee_subtype(self):
		auction = Auction(
			clinic=self.account,
			auctionStart=timezone.now(),
			auctionEnd=timezone.now() + timedelta(days=1),
			placementStart=timezone.localdate(),
			placementEnd=timezone.localdate() + timedelta(days=10),
			active=True,
			closed=False,
			deleted=False,
			cronID='cron-id',
			type=self.clinician_user_type,
			paymentType=self.fee_split,
			paymentTypes='Fee Split,Flat Fee',
			flatFeeType='hourly',
		)

		self.assertEqual(auction.get_payment_type_label(), 'Fee Split / Flat Fee (Hourly)')
		self.assertTrue(auction.is_fee_split())
		self.assertTrue(auction.is_flat_fee())

	def test_filter_and_badge_helpers_use_hourly_and_tcp_labels(self):
		hourly_auction = Auction(
			clinic=self.account,
			auctionStart=timezone.now(),
			auctionEnd=timezone.now() + timedelta(days=1),
			placementStart=timezone.localdate(),
			placementEnd=timezone.localdate() + timedelta(days=10),
			active=True,
			closed=False,
			deleted=False,
			cronID='cron-hourly',
			type=self.clinician_user_type,
			paymentType=self.fee_split,
			paymentTypes='Fee Split,Flat Fee',
			flatFeeType='hourly',
		)

		tcp_auction = Auction(
			clinic=self.account,
			auctionStart=timezone.now(),
			auctionEnd=timezone.now() + timedelta(days=1),
			placementStart=timezone.localdate(),
			placementEnd=timezone.localdate() + timedelta(days=10),
			active=True,
			closed=False,
			deleted=False,
			cronID='cron-tcp',
			type=self.clinician_user_type,
			paymentType=self.flat_fee,
			paymentTypes='Flat Fee',
			flatFeeType='total_contract',
		)

		self.assertEqual(hourly_auction.get_payment_type_filter_labels(), ['Fee Split', 'Flat Fee (hourly)'])
		self.assertEqual(hourly_auction.get_payment_type_badge_lines(), ['Fee Split', 'Flat Fee', '(Hourly)'])
		self.assertEqual(tcp_auction.get_payment_type_filter_labels(), ['Flat Fee (Total Contract Price)'])
		self.assertEqual(tcp_auction.get_payment_type_badge_lines(), ['Flat Fee', '(Total Contract Price)'])

	def test_effective_closed_when_listing_end_has_passed(self):
		expired_auction = Auction(
			clinic=self.account,
			auctionStart=timezone.now() - timedelta(days=3),
			auctionEnd=timezone.now() - timedelta(minutes=1),
			placementStart=timezone.localdate(),
			placementEnd=timezone.localdate() + timedelta(days=10),
			active=True,
			closed=False,
			deleted=False,
			cronID='expired-cron',
			type=self.clinician_user_type,
			paymentType=self.flat_fee,
			paymentTypes='Flat Fee',
			flatFeeType='hourly',
		)

		self.assertTrue(expired_auction.is_effectively_closed())
		self.assertFalse(expired_auction.is_effectively_active())

	def test_completed_card_uses_default_copy_without_winner(self):
		no_winner_auction = Auction(
			clinic=self.account,
			auctionStart=timezone.now() - timedelta(days=2),
			auctionEnd=timezone.now() - timedelta(days=1),
			placementStart=timezone.localdate(),
			placementEnd=timezone.localdate() + timedelta(days=10),
			active=False,
			closed=True,
			deleted=False,
			cronID='no-winner-cron',
			type=self.clinician_user_type,
			paymentType=self.flat_fee,
			paymentTypes='Flat Fee',
			flatFeeType='hourly',
		)

		self.assertFalse(no_winner_auction.has_winning_offer())
		self.assertEqual(no_winner_auction.get_winning_offer_symbol(), '$')
		self.assertEqual(no_winner_auction.get_completed_card_title(), 'Completed')


class DualOfferSubmissionTests(TestCase):
	def setUp(self):
		self.clinic_user_type = UserType.objects.create(name='Physiotherapy Clinic')
		self.clinician_user_type = UserType.objects.create(name='Physiotherapist')
		self.fee_split = PaymentType.objects.create(name='Fee Split')
		self.flat_fee = PaymentType.objects.create(name='Flat Fee')
		AdminSetting.objects.create(sendEmails=False, numAllowedAuctions=5, defaultAuctionLength=1209600, endAuctionEmailBatchSize=50)

		self.clinic_user = User.objects.create_user(
			username='clinic-submit@example.com',
			email='clinic-submit@example.com',
			password='password123',
		)
		self.clinic_account = Account.objects.get(user=self.clinic_user)
		self.clinic_account.clinicName = 'Dual Offer Clinic'
		self.clinic_account.userType = self.clinic_user_type
		self.clinic_account.save()

		self.therapist_user = User.objects.create_user(
			username='therapist-submit@example.com',
			email='therapist-submit@example.com',
			password='password123',
		)
		self.therapist_account = Account.objects.get(user=self.therapist_user)
		self.therapist_account.userType = self.clinician_user_type
		self.therapist_account.save()

		self.auction = Auction.objects.create(
			clinic=self.clinic_account,
			auctionStart=timezone.now(),
			auctionEnd=timezone.now() + timedelta(days=2),
			placementStart=timezone.localdate(),
			placementEnd=timezone.localdate() + timedelta(days=10),
			active=True,
			closed=False,
			deleted=False,
			cronID='dual-offer-cron',
			type=self.clinician_user_type,
			paymentType=self.fee_split,
			paymentTypes='Fee Split,Flat Fee',
			flatFeeType='hourly',
		)

	def test_dual_offer_submission_creates_two_typed_bids(self):
		self.client.force_login(self.therapist_user)

		response = self.client.post(reverse('auction', args=[self.auction.auctionID]), {
			'flatFeeAmount': '120',
			'feeSplitAmount': '55',
		})

		self.assertEqual(response.status_code, 302)
		bids = Bid.objects.filter(auction=self.auction, user=self.therapist_user).order_by('offerType')
		self.assertEqual(bids.count(), 2)
		self.assertEqual(list(bids.values_list('offerType', flat=True)), ['Fee Split', 'Flat Fee'])
		self.assertEqual(list(bids.values_list('amount', flat=True)), [55, 120])

	def test_practitioner_page_does_not_show_public_clinic_desired_offer_guidance(self):
		self.auction.desiredFeeSplitPercentage = 60
		self.auction.desiredFlatFeeTotalContract = 12000
		self.auction.save(update_fields=['desiredFeeSplitPercentage', 'desiredFlatFeeTotalContract'])

		self.client.force_login(self.therapist_user)
		response = self.client.get(reverse('auction', args=[self.auction.auctionID]))

		self.assertEqual(response.status_code, 200)
		content = response.content.decode('utf-8')
		self.assertNotIn('Fee Split: 60%', content)
		self.assertNotIn('Flat Fee (Total Contract Price): $12000', content)
