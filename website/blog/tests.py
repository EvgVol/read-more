from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from PIL import Image
from taggit.models import Tag

from .models import Post, Category

User = get_user_model()


def _tiny_image():
    buffer = BytesIO()
    Image.new('RGB', (10, 10), color='white').save(buffer, format='PNG')
    return SimpleUploadedFile('img.png', buffer.getvalue(),
                               content_type='image/png')


def _make_post(title, author, category=None, tag=None, published=True):
    post = Post.objects.create(
        title=title,
        author=author,
        body=f'Body of {title}',
        category=category,
        image=_tiny_image(),
        status=Post.Status.PUBLISHED if published
        else Post.Status.DRAFT,
    )
    if tag:
        post.tags.add(tag)
    return post


class TestPostList(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='author', email='a@example.com', password='pass123')

    def test_only_published_shown(self):
        pub = _make_post('Pub', self.user, published=True)
        draft = _make_post('Draft', self.user, published=False)
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        latest = list(response.context['latest_posts'])
        self.assertIn(pub, latest)
        self.assertNotIn(draft, latest)

    def test_filter_by_tag(self):
        tag = Tag.objects.create(name='python', slug='python')
        _make_post('Matched', self.user, tag=tag)
        _make_post('Other', self.user)
        response = self.client.get(
            reverse('blog:post_list_by_tag', args=['python']))
        self.assertEqual(response.status_code, 200)

    def test_unknown_tag_returns_404(self):
        response = self.client.get(
            reverse('blog:post_list_by_tag', args=['ghost']))
        self.assertEqual(response.status_code, 404)

    def test_filter_by_category(self):
        cat = Category.objects.create(name='Tech')
        _make_post('InCat', self.user, category=cat)
        response = self.client.get(
            reverse('blog:post_list_by_category', args=[cat.slug]))
        self.assertEqual(response.status_code, 200)


class TestPostDetail(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='author2', email='a2@example.com', password='pass123')

    def test_published_post_detail(self):
        post = _make_post('Detail', self.user, published=True)
        response = self.client.get(post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post'], post)

    def test_draft_post_detail_404(self):
        draft = _make_post('Hidden', self.user, published=False)
        response = self.client.get(draft.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_wrong_date_404(self):
        _make_post('Wrong', self.user, published=True)
        response = self.client.get(
            reverse('blog:post_detail',
                    args=['1999', '1', '1', 'wrong']))
        self.assertEqual(response.status_code, 404)


class TestPostLike(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='liker', email='l@example.com', password='pass123')
        self.client.login(username='liker', password='pass123')
        self.post = _make_post('Likeable', self.user)
        self.url = reverse('blog:post_like')

    def test_like_adds_user(self):
        response = self.client.post(
            self.url, data={'id': self.post.id, 'action': 'like'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertIn(self.user, self.post.users_like.all())

    def test_unlike_removes_user(self):
        self.post.users_like.add(self.user)
        response = self.client.post(
            self.url, data={'id': self.post.id, 'action': 'unlike'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.user, self.post.users_like.all())

    def test_like_unknown_post_returns_error(self):
        response = self.client.post(
            self.url, data={'id': 99999, 'action': 'like'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'error')

    def test_like_requires_login(self):
        self.client.logout()
        response = self.client.post(
            self.url, data={'id': self.post.id, 'action': 'like'})
        self.assertEqual(response.status_code, 302)


class TestCreatePost(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='writer', email='w@example.com', password='pass123')
        self.client.login(username='writer', password='pass123')
        self.category = Category.objects.create(name='News')

    def test_create_post_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('blog:post_create'))
        self.assertEqual(response.status_code, 302)

    def test_create_post(self):
        data = {
            'title': 'My First Post',
            'body': 'Hello world',
            'category': self.category.id,
            'tags': 'django, web',
            'image': _tiny_image(),
        }
        response = self.client.post(
            reverse('blog:post_create'), data=data)
        self.assertEqual(response.status_code, 302)
        post = Post.objects.get(title='My First Post')
        self.assertEqual(post.author, self.user)
        self.assertIn('django', [t.name for t in post.tags.all()])

    def test_create_post_invalid_renders_errors(self):
        response = self.client.post(
            reverse('blog:post_create'),
            data={'title': '', 'body': '', 'category': self.category.id,
                  'image': _tiny_image()})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(Post.objects.count(), 0)


class TestPostFeed(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='feeduser', email='f@example.com', password='pass123')

    def test_feed_returns_published(self):
        _make_post('Feed A', self.user, published=True)
        _make_post('Feed B', self.user, published=True)
        _make_post('Draft C', self.user, published=False)
        response = self.client.get(reverse('blog:post_feed'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Feed A', content)
        self.assertIn('Feed B', content)
        self.assertNotIn('Draft C', content)