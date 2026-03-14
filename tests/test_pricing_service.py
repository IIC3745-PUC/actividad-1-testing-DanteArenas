import unittest
from unittest.mock import Mock

from src.models import CartItem, Order
from src.pricing import PricingService, PricingError

class TestPricingService(unittest.TestCase):
	def setUp(self):
		self.ps = PricingService()

	def test_subtotal_cents(self):

		items = [
			CartItem(sku="A", unit_price_cents=100, qty=2),
			CartItem(sku="B", unit_price_cents=250, qty=3),
		]
		self.assertEqual(self.ps.subtotal_cents(items), 950)

	def test_invalid_qty_subtotal_cents(self):
		item = CartItem(sku="A", unit_price_cents=100, qty=0)
		with self.assertRaises(PricingError):
			self.ps.subtotal_cents([item])

	def test_invalid_unit_price_subtotal_cents(self):
		item = CartItem(sku="A", unit_price_cents=-100, qty=1)
		with self.assertRaises(PricingError):
			self.ps.subtotal_cents([item])

	def test_apply_coupon_no_descuento(self):
		self.assertEqual(self.ps.apply_coupon(1000, None), 1000)
		self.assertEqual(self.ps.apply_coupon(1000, ""), 1000)
		self.assertEqual(self.ps.apply_coupon(1000, "   "), 1000)

	def test_apply_coupon_save10(self):
		self.assertEqual(self.ps.apply_coupon(100, "SAVE10"), 90)

	def test_apply_coupon_clp2000(self):
		self.assertEqual(self.ps.apply_coupon(5000, "CLP2000"), 3000)
		self.assertEqual(self.ps.apply_coupon(1500, "CLP2000"), 0)

	def test_invalid_coupon(self):
		with self.assertRaises(PricingError):
			self.ps.apply_coupon(1000, "CUPONINVALIDOHOLA")

	def test_tax_cents_cl(self):
		self.assertEqual(self.ps.tax_cents(1000, "CL"), 190)
	
	def test_tax_cents_eu(self):
		self.assertEqual(self.ps.tax_cents(1000, "EU"), 210)

	def test_tax_cents_us(self):
		self.assertEqual(self.ps.tax_cents(1000, "US"), 0)

	def test_tax_cents_unsupported_country(self):
		with self.assertRaises(PricingError):
			self.ps.tax_cents(1000, "XD")

	def test_shipping_cents_cl(self):
		self.assertEqual(self.ps.shipping_cents(25000, "CL"), 0)
		self.assertEqual(self.ps.shipping_cents(15000, "CL"), 2500)

	def test_shipping_cents_us(self):
		self.assertEqual(self.ps.shipping_cents(1000, "US"), 5000)

	def test_shipping_cents_eu(self):
		self.assertEqual(self.ps.shipping_cents(1000, "EU"), 5000)

	def test_shipping_cents_unsupported_country(self):
		with self.assertRaises(PricingError):
			self.ps.shipping_cents(1000, "XD")

	def test_total_cents(self):
		total = self.ps.total_cents([
			CartItem(sku="A", unit_price_cents=100, qty=2),
			CartItem(sku="B", unit_price_cents=250, qty=3),
		], "SAVE10", "CL")
		self.assertEqual(total, 3517)


