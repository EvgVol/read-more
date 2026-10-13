from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse

from .models import Category, Product


def _make_product(name, category, price, available=True):
    return Product.objects.create(
        name=name, category=category, price=price, available=available)


class TestProductList(TestCase):
    """Tests for product_list view."""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Books')
        self.product_a = _make_product(
            'Product A', self.category, Decimal('10.00'))
        self.product_b = _make_product(
            'Product B', self.category, Decimal('20.00'))
        self.unavailable = _make_product(
            'Unavailable', self.category, Decimal('30.00'),
            available=False)

    def test_lists_only_available_products(self):
        response = self.client.get(reverse('shop:product_list'))
        self.assertEqual(response.status_code, 200)
        products = list(response.context['products'])
        self.assertIn(self.product_a, products)
        self.assertIn(self.product_b, products)
        self.assertNotIn(self.unavailable, products)

    def test_filter_by_category_slug(self):
        other_category = Category.objects.create(name='Audio')
        other_product = _make_product(
            'Other', other_category, Decimal('5.00'))

        response = self.client.get(
            reverse('shop:product_list_by_category',
                    args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)
        products = list(response.context['products'])
        self.assertIn(self.product_a, products)
        self.assertNotIn(other_product, products)

    def test_unknown_category_slug_returns_404(self):
        response = self.client.get(
            reverse('shop:product_list_by_category', args=['no-such-slug']))
        self.assertEqual(response.status_code, 404)


class TestProductDetail(TestCase):
    """Tests for product_detail view."""

    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Books')
        self.product = _make_product(
            'Product A', self.category, Decimal('10.00'))

    def test_returns_product_page(self):
        response = self.client.get(
            reverse('shop:product_detail',
                    args=[self.category.slug, self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['product'], self.product)

    def test_unavailable_product_returns_404(self):
        unavailable = _make_product(
            'Hidden', self.category, Decimal('1.00'), available=False)
        response = self.client.get(
            reverse('shop:product_detail',
                    args=[self.category.slug, unavailable.slug]))
        self.assertEqual(response.status_code, 404)

    def test_product_from_other_category_returns_404(self):
        other = Category.objects.create(name='Audio')
        response = self.client.get(
            reverse('shop:product_detail',
                    args=[other.slug, self.product.slug]))
        self.assertEqual(response.status_code, 404)