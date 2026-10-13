from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from PIL import Image as PILImage

from bookmarks.models import Image

User = get_user_model()


def _tiny_image():
    buffer = BytesIO()
    PILImage.new('RGB', (10, 10), color='white').save(buffer, format='PNG')
    return buffer.getvalue()


def _make_image(title='Bookmark', user=None):
    img = Image(title=title, user=user, url='https://example.com/a.png')
    img.image.save('a.png', SimpleUploadedFile(
        'a.png', _tiny_image(), content_type='image/png'), save=False)
    img.save()
    return img


class TestImageList(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='bm', email='bm@example.com', password='pass123')
        self.image = _make_image(user=self.user)

    def test_list_requires_login(self):
        response = self.client.get(reverse('bookmarks:list'))
        self.assertEqual(response.status_code, 302)

    def test_list_shows_images(self):
        self.client.login(username='bm', password='pass123')
        response = self.client.get(reverse('bookmarks:list'))
        self.assertEqual(response.status_code, 200)


class TestImageDetail(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='bmd', email='bmd@example.com', password='pass123')
        self.image = _make_image(user=self.user)

    def test_detail_renders(self):
        response = self.client.get(
            reverse('bookmarks:detail',
                    args=[self.image.id, self.image.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['image'], self.image)

    def test_detail_wrong_id_404(self):
        response = self.client.get(
            reverse('bookmarks:detail', args=[99999, self.image.slug]))
        self.assertEqual(response.status_code, 404)

    def test_detail_wrong_slug_404(self):
        response = self.client.get(
            reverse('bookmarks:detail', args=[self.image.id, 'wrong-slug']))
        self.assertEqual(response.status_code, 404)


class TestImageLike(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='bmlike', email='bmlike@example.com', password='pass123')
        self.client.login(username='bmlike', password='pass123')
        self.image = _make_image(user=self.user)
        self.url = reverse('bookmarks:like')

    def test_like_returns_ok(self):
        response = self.client.post(
            self.url, data={'id': self.image.id, 'action': 'like'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertIn(self.user, self.image.users_like.all())

    def test_unlike_removes_and_returns_ok(self):
        self.image.users_like.add(self.user)
        response = self.client.post(
            self.url, data={'id': self.image.id, 'action': 'unlike'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertNotIn(self.user, self.image.users_like.all())

    def test_unknown_image_returns_error(self):
        response = self.client.post(
            self.url, data={'id': 99999, 'action': 'like'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'error')

    def test_like_requires_login(self):
        self.client.logout()
        response = self.client.post(
            self.url, data={'id': self.image.id, 'action': 'like'})
        self.assertEqual(response.status_code, 302)


class TestImageSlug(TestCase):
    def test_slug_auto_generated_from_title(self):
        user = User.objects.create_user(
            username='slugg', email='slugg@example.com', password='pass123')
        image = _make_image(title='Beautiful View', user=user)
        self.assertEqual(image.slug, 'beautiful-view')


class TestImageLikeCsrf(TestCase):
    """image_like must enforce CSRF now that @csrf_exempt is gone."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='likecs', email='lcs@example.com', password='pass123')
        self.image = _make_image(user=self.user)
        self.url = reverse('bookmarks:like')

    def _client(self):
        return Client(enforce_csrf_checks=True)

    def test_post_with_valid_token_ok(self):
        c = self._client()
        c.login(username='likecs', password='pass123')
        # profile-edit form renders {% csrf_token %} for this session
        c.get(reverse('account_edit'))
        token = c.cookies['csrftoken'].value
        response = c.post(
            self.url, data={'id': self.image.id, 'action': 'like'},
            HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertIn(self.user, self.image.users_like.all())

    def test_post_without_token_rejected_403(self):
        c = self._client()
        c.login(username='likecs', password='pass123')
        c.get(reverse('account_edit'))
        response = c.post(
            self.url, data={'id': self.image.id, 'action': 'like'})
        self.assertEqual(response.status_code, 403)