from decimal import Decimal
from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from .cart import Cart
from shop.models import Category, Product

User = get_user_model()


def _make_product(name, price):
    category = Category.objects.create(name=f'cat-{name}')
    return Product.objects.create(
        name=name, category=category, price=price)


class TestCartModel(TestCase):
    """Tests for the Cart class."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='cartuser',
            email='cart@example.com',
            password='pass123',
        )
        self.client.login(username='cartuser', password='pass123')
        self.product = _make_product('Book', Decimal('10.00'))

    def _cart(self):
        request = SimpleNamespace(session=self.client.session)
        return Cart(request)

    def test_empty_cart(self):
        cart = self._cart()
        self.assertEqual(len(cart), 0)
        self.assertEqual(cart.get_total_price(), Decimal('0'))

    def test_add_product_to_cart(self):
        cart = self._cart()
        cart.add(product=self.product, quantity=2)
        self.assertEqual(len(cart), 2)
        self.assertEqual(cart.get_total_price(), Decimal('20.00'))
        self.assertEqual(cart.get_unique_products, 1)

    def test_add_same_product_twice_increases_quantity(self):
        cart = self._cart()
        cart.add(product=self.product, quantity=1)
        cart.add(product=self.product, quantity=1)
        self.assertEqual(len(cart), 2)

    def test_remove_product_from_cart(self):
        cart = self._cart()
        cart.add(product=self.product, quantity=1)
        cart.remove(product=self.product)
        self.assertEqual(len(cart), 0)

    def test_clear_cart(self):
        cart = self._cart()
        cart.add(product=self.product, quantity=1)
        cart.clear()
        # clear() removes the session key; re-read a fresh cart to verify
        self.assertEqual(len(self._cart()), 0)


class TestCartViews(TestCase):
    """Tests for cart views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='cartuser2',
            email='cart2@example.com',
            password='pass123',
        )
        self.client.login(username='cartuser2', password='pass123')
        self.product = _make_product('Book2', Decimal('15.00'))

    def test_cart_detail_renders_cart(self):
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['cart']), 0)

    def test_cart_add_product(self):
        response = self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            data={'quantity': 2, 'override': False})
        self.assertEqual(response.status_code, 302)
        request = SimpleNamespace(session=self.client.session)
        cart = Cart(request)
        self.assertEqual(len(cart), 2)
        self.assertEqual(cart.get_total_price(), Decimal('30.00'))

    def test_cart_add_requires_post(self):
        response = self.client.get(
            reverse('cart:cart_add', args=[self.product.id]))
        self.assertEqual(response.status_code, 405)

    def test_cart_remove_product(self):
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            data={'quantity': 1, 'override': False})
        response = self.client.post(
            reverse('cart:cart_remove', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        request = SimpleNamespace(session=self.client.session)
        cart = Cart(request)
        self.assertEqual(len(cart), 0)

    def test_cart_clear(self):
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            data={'quantity': 1, 'override': False})
        response = self.client.post(reverse('cart:cart_clear'))
        self.assertEqual(response.status_code, 302)
        request = SimpleNamespace(session=self.client.session)
        cart = Cart(request)
        self.assertEqual(len(cart), 0)