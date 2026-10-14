from io import BytesIO
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from io import StringIO
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


class TestCleanupOldActions(TestCase):
    """Tests for the cleanup_old_actions management command."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='actor', email='act@example.com', password='pass123')
        # one fresh action, one 100 days old
        create_action(self.user, 'fresh verb')
        create_action(self.user, 'old verb')
        self.old = Action.objects.get(verb='old verb')
        Action.objects.filter(pk=self.old.pk).update(
            created=timezone.now() - timedelta(days=100))
        self.old.refresh_from_db()

    def _run(self, *args):
        out = StringIO()
        call_command('cleanup_old_actions', *args, stdout=out)
        return out.getvalue()

    def test_dry_run_does_not_delete(self):
        output = self._run('--days', '90')
        self.assertEqual(Action.objects.count(), 2)
        self.assertIn('1', output)  # reports 1 deletable

    def test_apply_deletes_only_stale(self):
        output = self._run('--days', '90', '--apply')
        remaining = list(Action.objects.values_list('verb', flat=True))
        self.assertEqual(remaining, ['fresh verb'])
        self.assertIn('1', output)

    def test_custom_days_window(self):
        # 100-day-old action is "fresh" under a 365-day window
        output = self._run('--days', '365', '--apply')
        self.assertEqual(Action.objects.count(), 2)
        self.assertIn('0', output)

    def test_days_below_one_rejected(self):
        out = StringIO()
        err = StringIO()
        call_command('cleanup_old_actions', '--days', '0', stdout=out,
                     stderr=err)
        self.assertIn('1', err.getvalue())
        self.assertEqual(Action.objects.count(), 2)