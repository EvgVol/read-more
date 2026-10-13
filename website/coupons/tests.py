from datetime import timedelta
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from cart.cart import Cart
from shop.models import Category, Product
from .models import Coupon


def _make_coupon(code, discount=10, days_ago=7, days_left=7, active=True):
    now = timezone.now()
    return Coupon.objects.create(
        code=code,
        discount=discount,
        valid_from=now - timedelta(days=days_ago),
        valid_to=now + timedelta(days=days_left),
        active=active,
    )


class TestCouponApply(TestCase):
    """Tests for the coupon_apply view."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('coupons:apply')

    def test_apply_valid_coupon(self):
        coupon = _make_coupon('SAVE10')
        response = self.client.post(self.url, data={'code': 'SAVE10'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['coupon_id'], coupon.id)

    def test_apply_is_case_insensitive(self):
        coupon = _make_coupon('SAVE10')
        response = self.client.post(self.url, data={'code': 'save10'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session['coupon_id'], coupon.id)

    def test_expired_coupon_rejected(self):
        _make_coupon('EXPIRED', days_ago=10, days_left=-3)
        response = self.client.post(self.url, data={'code': 'EXPIRED'})
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(self.client.session.get('coupon_id'))

    def test_not_yet_valid_coupon_rejected(self):
        _make_coupon('FUTURE', days_ago=-7, days_left=14)
        response = self.client.post(self.url, data={'code': 'FUTURE'})
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(self.client.session.get('coupon_id'))

    def test_inactive_coupon_rejected(self):
        _make_coupon('OFF', active=False)
        response = self.client.post(self.url, data={'code': 'OFF'})
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(self.client.session.get('coupon_id'))

    def test_unknown_code_rejected(self):
        response = self.client.post(self.url, data={'code': 'NOPE'})
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(self.client.session.get('coupon_id'))

    def test_invalid_form_keeps_session_untouched(self):
        _make_coupon('SAVE10')
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('coupon_id', self.client.session)

    def test_apply_requires_post(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


class TestCartCoupon(TestCase):
    """Tests for the Coupon property of Cart."""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Books')
        self.product = Product.objects.create(
            name='Book', category=self.category, price='20.00')

    def _cart(self):
        from types import SimpleNamespace
        return Cart(SimpleNamespace(session=self.client.session))

    def test_cart_with_applied_coupon(self):
        coupon = _make_coupon('SAVE10', discount=10)
        session = self.client.session
        session['coupon_id'] = coupon.id
        session.save()
        cart = self._cart()
        cart.add(product=self.product, quantity=2)
        self.assertEqual(cart.coupon, coupon)
        self.assertEqual(cart.get_total_price(), Decimal('40.00'))
        self.assertEqual(cart.get_discount(), Decimal('4.00'))
        self.assertEqual(cart.get_total_price_after_discount(), Decimal('36.00'))

    def test_cart_without_coupon(self):
        cart = self._cart()
        cart.add(product=self.product, quantity=2)
        self.assertIsNone(cart.coupon)
        self.assertEqual(cart.get_discount(), 0)

    def test_cart_with_deleted_coupon_falls_back_to_none(self):
        coupon = _make_coupon('GONE')
        session = self.client.session
        session['coupon_id'] = coupon.id
        session.save()
        coupon.delete()
        cart = self._cart()
        self.assertIsNone(cart.coupon)