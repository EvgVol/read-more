from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from .models import Profile, Contact

User = get_user_model()


class TestRegister(TestCase):
    """Tests for the register view."""

    def _register_data(self, **overrides):
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'secret123',
            'privacy_policy': 'on',
        }
        data.update(overrides)
        return data

    def test_register_creates_user_and_profile(self):
        response = self.client.post(
            reverse('signup'), data=self._register_data())
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='newuser')
        self.assertTrue(user.check_password('secret123'))
        self.assertTrue(
            Profile.objects.filter(user=user).exists())

    def test_register_without_policy_renders_errors(self):
        response = self.client.post(
            reverse('signup'),
            data=self._register_data(privacy_policy=''))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(
            username='newuser').exists())
        self.assertIn('privacy_policy', response.context['form'].errors)

    def test_register_duplicate_email_renders_errors(self):
        User.objects.create_user(
            username='other', email='new@example.com', password='x')
        response = self.client.post(
            reverse('signup'), data=self._register_data())
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['form'].errors)

    def test_register_invalid_username_renders_errors(self):
        response = self.client.post(
            reverse('signup'), data=self._register_data(username='me'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('username', response.context['form'].errors)


class TestUserDetail(TestCase):
    """Tests for the user_detail view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='detail_user', email='d@example.com',
            password='pass123')
        self.client.login(username='detail_user', password='pass123')

    def test_requires_login(self):
        self.client.logout()
        response = self.client.get(
            reverse('profile', args=['detail_user']))
        self.assertEqual(response.status_code, 302)

    def test_returns_profile_page(self):
        response = self.client.get(
            reverse('profile', args=['detail_user']))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['author'], self.user)

    def test_inactive_user_returns_404(self):
        inactive = User.objects.create_user(
            username='inactive_user', email='i@example.com',
            password='pass123', is_active=False)
        response = self.client.get(
            reverse('profile', args=['inactive_user']))
        self.assertEqual(response.status_code, 404)

    def test_unknown_user_returns_404(self):
        response = self.client.get(reverse('profile', args=['ghost']))
        self.assertEqual(response.status_code, 404)


class TestUserEdit(TestCase):
    """Tests for the user_edit view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='edit_user', email='e@example.com',
            password='pass123')
        self.client.login(username='edit_user', password='pass123')
        self.valid_data = {
            'save-details': '',
            'username': 'edit_user',
            'email': 'e@example.com',
            'first_name': 'Evgeniy',
            'last_name': 'Volochek',
            'birthdate': '1990-01-01',
            'phone_number': '89001234567',
            'about_me': 'QA engineer',
        }

    def _post(self, data):
        return self.client.post(reverse('account_edit'), data=data)

    def test_edit_saves_profile(self):
        response = self._post(self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Evgeniy')
        self.assertEqual(self.user.phone_number, '89001234567')

    def test_edit_rejects_future_birthdate(self):
        future = (date.today() + timedelta(days=1)).isoformat()
        response = self._post(self.valid_data | {'birthdate': future})
        self.assertEqual(response.status_code, 200)
        self.assertIn('birthdate', response.context['form'].errors)

    def test_edit_rejects_non_digit_phone(self):
        response = self._post(
            self.valid_data | {'phone_number': '8-900-abcd'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('phone_number', response.context['form'].errors)

    def test_edit_rejects_taken_username(self):
        User.objects.create_user(
            username='taken', email='t@example.com', password='x')
        response = self._post(self.valid_data | {'username': 'taken'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('username', response.context['form'].errors)

    def test_edit_rejects_taken_email(self):
        User.objects.create_user(
            username='taken2', email='shared@example.com', password='x')
        response = self._post(
            self.valid_data | {'email': 'shared@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('email', response.context['form'].errors)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'e@example.com')


class TestUserList(TestCase):
    """Tests for the user_list view (staff only)."""

    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user(
            username='boss', email='boss@example.com',
            password='pass123', is_staff=True)
        self.normal = User.objects.create_user(
            username='pleb', email='pleb@example.com',
            password='pass123')

    def test_non_staff_cannot_see_user_list(self):
        self.client.login(username='pleb', password='pass123')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 302)

    def test_staff_sees_user_list(self):
        self.client.login(username='boss', password='pass123')
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        users = list(response.context['users'])
        self.assertIn(self.staff, users)
        self.assertIn(self.normal, users)


class TestUserFollow(TestCase):
    """Tests for the user_follow view."""

    def setUp(self):
        self.client = Client()
        self.follower = User.objects.create_user(
            username='follower', email='f@example.com',
            password='pass123')
        self.followed = User.objects.create_user(
            username='followed', email='f2@example.com',
            password='pass123')
        self.client.login(username='follower', password='pass123')
        self.url = reverse('user_follow')

    def test_follow_creates_contact(self):
        response = self.client.post(self.url, data={
            'id': self.followed.id, 'action': 'follow'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertTrue(Contact.objects.filter(
            user_from=self.follower,
            user_to=self.followed).exists())

    def test_unfollow_removes_contact(self):
        Contact.objects.create(
            user_from=self.follower, user_to=self.followed)
        response = self.client.post(self.url, data={
            'id': self.followed.id, 'action': 'unfollow'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Contact.objects.filter(
            user_from=self.follower,
            user_to=self.followed).exists())

    def test_follow_unknown_user_returns_error(self):
        response = self.client.post(
            self.url, data={'id': 99999, 'action': 'follow'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'error')

    def test_follow_requires_login(self):
        self.client.logout()
        response = self.client.post(self.url, data={
            'id': self.followed.id, 'action': 'follow'})
        self.assertEqual(response.status_code, 302)