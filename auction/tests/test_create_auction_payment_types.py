from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from auction.forms import AuctionForm
from auction.models import Account, Auction, PaymentType, UserType


class AuctionPaymentTypeFormTests(TestCase):
	def setUp(self):
		self.clinic_user_type = UserType.objects.create(name='Physiotherapy Clinic')
		self.clinician_user_type = UserType.objects.create(name='Physiotherapist')
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
