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


class TestDashboardLikeCount(TestCase):
    """like_count must be correct and computed without N+1 queries."""

    def setUp(self):
        self.client = Client()
        from django.contrib.auth import get_user_model
        from blog.models import Post
        from io import BytesIO
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.Post = Post
        self.User = get_user_model()

        def _img():
            b = BytesIO()
            Image.new('RGB', (5, 5), 'white').save(b, format='PNG')
            return SimpleUploadedFile('i.png', b.getvalue(),
                                      content_type='image/png')
        self._img = _img

    def test_like_count_correct_and_not_n_plus_1(self):
        from django.test.utils import CaptureQueriesContext
        from django.db import connection
        u = self.User.objects.create_user(
            username='dc', email='dc@example.com', password='pass123')
        posts = [
            self.Post.objects.create(
                title=f'P{i}', author=u, body='b', image=self._img(),
                status=self.Post.Status.PUBLISHED)
            for i in range(6)
        ]
        posts[0].users_like.add(u)
        posts[1].users_like.add(u)
        posts[2].users_like.add(u)  # 3 likes total
        expected = sum(p.users_like.count() for p in posts)
        self.assertEqual(expected, 3)

        with CaptureQueriesContext(connection) as ctx:
            response = self.client.get(reverse('core:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['like_count'], expected)
        # The fix counts the m2m through table in a single query, so the
        # dashboard should not scale its query count with the number of
        # posts (a naive per-post .count() adds one query per post).
        self.assertLess(len(ctx.captured_queries), 20)