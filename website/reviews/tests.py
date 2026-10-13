from io import BytesIO

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.test import TestCase, Client
from django.urls import reverse
from PIL import Image

from blog.models import Post
from shop.models import Category, Product

from .models import Review
from .forms import ReviewForm

User = get_user_model()


def _tiny_image():
    buffer = BytesIO()
    Image.new('RGB', (10, 10), color='white').save(buffer, format='PNG')
    return SimpleUploadedFile('img.png', buffer.getvalue(),
                               content_type='image/png')


def _make_product(name='Book'):
    cat = Category.objects.create(name=f'cat-{name}')
    return Product.objects.create(
        name=name, category=cat, price='10.00', image=_tiny_image())


class TestReviewModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='reviewer', email='r@example.com', password='pass123')
        self.product = _make_product()

    def test_review_with_comment_saves(self):
        review = Review(author=self.user, content_object=self.product,
                        comment='Nice book')
        review.save()
        review = Review.objects.get()
        self.assertEqual(review.author, self.user)
        self.assertEqual(review.content_object, self.product)

    def test_review_with_rating_saves(self):
        review = Review(author=self.user, content_object=self.product,
                        rating=5)
        review.save()
        self.assertEqual(Review.objects.get().rating, 5)

    def test_review_empty_rating_and_comment_raises(self):
        review = Review(author=self.user, content_object=self.product)
        with self.assertRaises(ValidationError):
            review.save()
        self.assertEqual(Review.objects.count(), 0)


class TestReviewForm(TestCase):
    def test_form_accepts_valid(self):
        form = ReviewForm(data={'comment': 'Good'})
        self.assertTrue(form.is_valid())

    def test_form_rejects_empty(self):
        form = ReviewForm(data={})
        self.assertFalse(form.is_valid())


class TestCreateReviewView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='reviewer2', email='r2@example.com', password='pass123')
        self.client.login(username='reviewer2', password='pass123')
        self.product = _make_product()
        self.ct = ContentType.objects.get_for_model(Product)
        self.url = reverse(
            'reviews:create_review',
            args=[self.ct.id, self.product.id])

    def test_create_review_success(self):
        response = self.client.post(
            self.url, data={'comment': 'Great product'})
        self.assertEqual(response.status_code, 302)
        review = Review.objects.get()
        self.assertEqual(review.author, self.user)
        self.assertEqual(review.content_object, self.product)

    def test_create_review_requires_login(self):
        self.client.logout()
        response = self.client.post(
            self.url, data={'comment': 'Great'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 0)

    def test_create_review_requires_post(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_create_review_invalid_form_creates_nothing(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 0)

    def test_unknown_content_object_404(self):
        response = self.client.post(
            reverse('reviews:create_review',
                    args=[self.ct.id, 99999]),
            data={'comment': 'x'})
        self.assertEqual(response.status_code, 404)