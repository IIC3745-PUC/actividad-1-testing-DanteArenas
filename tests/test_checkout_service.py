import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError
from src.checkout import CheckoutService, ChargeResult

class TestCheckoutService(unittest.TestCase):
	def setUp(self):
		self.payments = Mock()
		self.email = Mock()
		self.fraud = Mock()
		self.repo = Mock()
		self.pricing = Mock()
		self.cs = CheckoutService(
			payments=self.payments,
			email=self.email,
			fraud=self.fraud,
			repo=self.repo,
			pricing=self.pricing,
		)

	def test_invalid_user(self):
		resultado = self.cs.checkout(
			user_id="",
			items=[CartItem(sku="A", unit_price_cents=100, qty=1)],
			payment_token="token",
			country="CL",
		)
		self.assertEqual(resultado, "INVALID_USER")

	def test_invalid_cart(self):
		self.pricing.total_cents.side_effect = PricingError("error")
		resultado = self.cs.checkout(
			user_id="123",
			items=[CartItem(sku="A", unit_price_cents=-100, qty=1)],
			payment_token="token",
			country="CL",
		)
		self.assertEqual(resultado, "INVALID_CART:error")

	def test_rejected_fraud(self):
		self.pricing.total_cents.return_value = 1000
		self.fraud.score.return_value = 100
		resultado = self.cs.checkout(
			user_id="123",
			items=[CartItem(sku="A", unit_price_cents=100, qty=1)],
			payment_token="token",
			country="CL",
		)
		self.assertEqual(resultado, "REJECTED_FRAUD")
	
	def test_payment_failed(self):
		self.pricing.total_cents.return_value = 1000
		self.fraud.score.return_value = 0
		self.payments.charge.return_value = ChargeResult(ok=False, charge_id=None, reason="no tienes plata")

		resultado = self.cs.checkout(
			user_id="123",
			items=[CartItem(sku="A", unit_price_cents=100, qty=1)],
			payment_token="token",
			country="CL",
		)
		self.assertEqual(resultado, "PAYMENT_FAILED:no tienes plata")

	def test_checkout_ok(self):
		self.pricing.total_cents.return_value = 1000
		self.fraud.score.return_value = 0
		self.payments.charge.return_value = ChargeResult(ok=True, charge_id="123")

		resultado = self.cs.checkout(
			user_id="123",
			items=[CartItem(sku="A", unit_price_cents=100, qty=1)],
			payment_token="token",
			country="CL",
		)

		self.assertTrue(resultado.startswith("OK:"))
