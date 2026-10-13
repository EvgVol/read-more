from django.test import TestCase, Client
from django.urls import reverse

from .models import Policy, Question


class TestPolicyManager(TestCase):
    def test_published_manager_filters_current_only(self):
        current = Policy.objects.create(
            body='Current policy', slug='current',
            status=Policy.Status.CURRENT)
        invalid = Policy.objects.create(
            body='Old policy', slug='old',
            status=Policy.Status.INVALID)

        published = list(Policy.published.all())
        self.assertIn(current, published)
        self.assertNotIn(invalid, published)
        # default manager returns everything
        self.assertEqual(Policy.objects.count(), 2)


class TestPolicyView(TestCase):
    def test_policy_view_lists_current(self):
        client = Client()
        Policy.objects.create(
            body='Current', slug='cur', status=Policy.Status.CURRENT)
        Policy.objects.create(
            body='Old', slug='old', status=Policy.Status.INVALID)
        response = client.get(reverse('core:policy'))
        self.assertEqual(response.status_code, 200)
        # the ListView uses the default manager -> shows both
        self.assertEqual(response.context['object_list'].count(), 2)


class TestQuestion(TestCase):
    def test_str(self):
        q = Question.objects.create(
            first_name='Evg', email='q@example.com', content='Why?')
        self.assertIn('Question', str(q))

    def test_ordering_newest_first(self):
        q1 = Question.objects.create(
            first_name='A', email='a@example.com', content='c1')
        q2 = Question.objects.create(
            first_name='B', email='b@example.com', content='c2')
        ordered = list(Question.objects.all())
        self.assertEqual(ordered[0], q2)
        self.assertEqual(ordered[1], q1)


class TestErrorViews(TestCase):
    """Custom error handlers (core.views) return the proper status codes."""

    def test_404_handler(self):
        response = self.client.get('/this-path-does-not-exist-xyz/')
        self.assertEqual(response.status_code, 404)

    def test_permission_denied_handler_returns_403(self):
        from django.test import RequestFactory
        from django.core.exceptions import PermissionDenied
        from django.contrib.sessions.middleware import SessionMiddleware
        from core.views import permission_denied
        request = RequestFactory().get('/ru/notification/')
        SessionMiddleware(lambda r: None).process_request(request)
        response = permission_denied(request, PermissionDenied())
        self.assertEqual(response.status_code, 403)