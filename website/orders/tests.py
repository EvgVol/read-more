from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase, Client
from django.urls import reverse

from shop.models import Category, Product
from orders.models import Order, OrderItem
from orders.tasks import order_created


def _add_product_to_session(client, product, quantity=1):
    """Добавить товар в сессию (корзину) напрямую."""
    session = client.session
    cart = session.get('cart', {})
    cart[str(product.id)] = {
        'quantity': quantity, 'price': str(product.price)
    }
    session['cart'] = cart
    session.save()


class TestOrderCreate(TestCase):
    """Tests for the order_create() function."""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Books')
        self.product = Product.objects.create(
            name='Django for Professionals',
            category=self.category,
            price=Decimal('10.00'),
        )
        self.data = {
            'first_name': 'Evgeniy',
            'last_name': 'Volochek',
            'email': 'evgvol@example.com',
            'address': '24 Leningradskay St',
            'postal_code': '443000',
            'city': 'Samara',
        }

    @patch('orders.views.order_created.delay')
    def test_order_create_valid_data(self, mock_delay):
        """Valid form data renders the invoice with a success message."""
        response = self.client.post(
            reverse('orders:order_create'), data=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'Your order has been placed successfully')
        self.assertTrue(Order.objects.exists())

    def test_order_create_invalid_data(self):
        """Invalid form data re-renders checkout with form errors."""
        response = self.client.post(
            reverse('orders:order_create'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertFalse(Order.objects.exists())

    @patch('orders.views.order_created.delay')
    def test_order_create_create_order(self, mock_delay):
        """The function creates an order and an order item from the cart."""
        _add_product_to_session(self.client, self.product)
        response = self.client.post(
            reverse('orders:order_create'), data=self.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        order = Order.objects.get()
        self.assertEqual(order.first_name, self.data['first_name'])

    @patch('orders.views.order_created.delay')
    def test_order_create_clear_cart(self, mock_delay):
        """The cart is cleared after creating an order."""
        _add_product_to_session(self.client, self.product)
        response = self.client.post(
            reverse('orders:order_create'), data=self.data)
        self.assertEqual(response.status_code, 200)
        session_cart = self.client.session.get('cart', {})
        self.assertNotIn(str(self.product.id), session_cart)

    @patch('orders.views.order_created.delay')
    def test_order_create_enqueues_task(self, mock_delay):
        """order_created.delay is enqueued with the created order id."""
        response = self.client.post(
            reverse('orders:order_create'), data=self.data)
        self.assertEqual(response.status_code, 200)
        order = Order.objects.get()
        mock_delay.assert_called_once_with(order.id)


class TestOrderCreatedTask(TestCase):
    """Tests for the order_created() celery task."""

    def setUp(self):
        self.order = Order.objects.create(
            first_name='Evgeniy',
            last_name='Volochek',
            email='evgvol@example.com',
            address='24 Leningradskay St',
            postal_code='443000',
            city='Samara',
        )

    def test_order_created_sends_mail(self):
        """The task sends a confirmation email to the customer."""
        with patch('orders.tasks.send_mail', return_value=1) as mock_send:
            result = order_created(self.order.id)
        self.assertEqual(result, 1)
        mock_send.assert_called_once()
        args = mock_send.call_args[0]
        self.assertEqual(args[0], f'Order nr. {self.order.id}')
        self.assertEqual(args[3], [self.order.email])

    def test_order_created_missing_order(self):
        """The task raises Order.DoesNotExist for a non-existent order."""
        with self.assertRaises(Order.DoesNotExist):
            order_created(99999)