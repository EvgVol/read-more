import django
django.setup()

from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from cart.cart import Cart
from orders.models import Order, OrderItem


class TestOrderCreate(TestCase):
    """Tests for the order_create() function."""
    def setUp(self):
        self.client = Client()

    def test_order_create_valid_data(self):
        """Test that the function responds with an HTTP 200 code 
        when form data is valid."""
        data = {
            'first_name': 'Evgeniy',
            'last_name': 'Volochek',
            'email': 'evgvol@example.com',
            'address': '24 Leningradskay St',
            'postal_code': '443000',
            'city': 'Samara',
        }
        response = self.client.post(reverse('orders:order_create'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('Success! Your order has been placed.'))

    def test_order_create_invalid_data(self):
        """Test that the function responds with an HTTP 400 code 
        when form data is invalid."""
        response = self.client.post(reverse('orders:order_create'), data={})
        self.assertEqual(response.status_code, 400)

    def test_order_create_create_order(self):
        """Test that the function successfully creates a new order."""
        cart = Cart(self.client.session)
        cart.add(product_id=1, quantity=1, update_quantity=False)
        data = {
            'first_name': 'Evgeniy',
            'last_name': 'Volochek',
            'email': 'evgvol@example.com',
            'address': '24 Leningradskay St',
            'postal_code': '443000',
            'city': 'Samara',
        }
        response = self.client.post(reverse('orders:order_create'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)

    def test_order_create_clear_cart(self):
        """Test that the function successfully clears the cart after 
        creating an order."""
        cart = Cart(self.client.session)
        cart.add(product_id=1, quantity=1, update_quantity=False)
        data = {
            'first_name': 'Evgeniy',
            'last_name': 'Volochek',
            'email': 'evgvol@example.com',
            'address': '24 Leningradskay St',
            'postal_code': '443000',
            'city': 'Samara',
        }
        response = self.client.post(reverse('orders:order_create'), data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(cart.__len__(), 0)