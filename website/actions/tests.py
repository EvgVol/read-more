from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from PIL import Image

from blog.models import Post
from .utils import create_action
from .models import Action

User = get_user_model()


def _tiny_image():
    buffer = BytesIO()
    Image.new('RGB', (10, 10), color='white').save(buffer, format='PNG')
    return SimpleUploadedFile('img.png', buffer.getvalue(),
                               content_type='image/png')


class TestCreateAction(TestCase):
    """Tests for the create_action utility."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='actor', email='act@example.com', password='pass123')
        self.post = Post.objects.create(
            title='Target', author=self.user, body='b', image=_tiny_image(),
            category=None)

    def test_create_action_with_target(self):
        result = create_action(self.user, 'liked the post:', self.post)
        self.assertTrue(result)
        action = Action.objects.get()
        self.assertEqual(action.user, self.user)
        self.assertEqual(action.target, self.post)

    def test_create_action_without_target(self):
        result = create_action(self.user, 'cleared the cart')
        self.assertTrue(result)
        action = Action.objects.get()
        self.assertIsNone(action.target)

    def test_duplicate_action_within_minute_returns_false(self):
        first = create_action(self.user, 'verbed', self.post)
        second = create_action(self.user, 'verbed', self.post)
        self.assertTrue(first)
        self.assertFalse(second)
        self.assertEqual(Action.objects.count(), 1)

    def test_same_verb_different_targets_creates_both(self):
        post2 = Post.objects.create(
            title='Target2', author=self.user, body='b',
            image=_tiny_image(), category=None)
        create_action(self.user, 'verbed', self.post)
        create_action(self.user, 'verbed', post2)
        self.assertEqual(Action.objects.count(), 2)


class TestActionDashboard(TestCase):
    """Tests for the actions dashboard view."""

    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user(
            username='staff', email='st@example.com', password='pass123',
            is_staff=True)
        self.regular = User.objects.create_user(
            username='regular', email='rg@example.com', password='pass123')

    def test_requires_login(self):
        response = self.client.get(reverse('actions:notification'))
        self.assertEqual(response.status_code, 302)

    def test_non_staff_redirected_to_login(self):
        # @user_passes_test(is_staff) bounces authenticated non-staff
        create_action(self.regular, 'regular verb')
        self.client.login(username='regular', password='pass123')
        response = self.client.get(reverse('actions:notification'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_staff_sees_all_actions(self):
        create_action(self.staff, 'staff verb')
        create_action(self.regular, 'regular verb')
        self.client.login(username='staff', password='pass123')
        response = self.client.get(reverse('actions:notification'))
        self.assertEqual(response.status_code, 200)
        actions = list(response.context['actions'])
        self.assertEqual(len(actions), 2)